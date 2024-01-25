import glob
from datetime import datetime

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("要介護認定率・後期高齢者率出力")],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu ",
        ),
        dbc.Row(
            [
                dcc.Graph(
                    id="certification_rate_graph",
                    style={"height": "80vh"},
                ),
            ]
        ),
    ],
)

settings = html.Div(
    children=[
        dbc.Row(
            dbc.Button(
                href="/",
                children="戻る",
                className=" text-white back_button",
                external_link="true",
                color="dark",
            ),
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        html.P(
                            "オプション",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "0",
                                "fontSize": "1.3em",
                            },
                            className="font-weight-bold",
                        ),
                        html.Hr(),
                        html.P(
                            "集計対象選択",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="target_select",
                            options=[
                                {"label": "行政区", "value": "行政区"},
                                {"label": "小学校区", "value": "小学校区"},
                            ],
                            value="行政区",
                            className="setting_dropdown",
                            placeholder="集計対象選択",
                        ),
                        html.P(
                            "集計対象区選択",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="ward_select",
                            options=[
                                {"label": "全て", "value": "全て"},
                            ],
                            value="全て",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="集計対象区選択",
                        ),
                        dbc.Button(
                            href="#",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "35vh", "marginLeft": "1px"},
        ),
    ]
)

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    settings,
                    className="bg-light",
                    width=2,
                ),
                dbc.Col(
                    contents,
                    width=10,
                ),
            ]
        )
    ]
)


def load_and_process_files():
    files = glob.glob("/usr/src/data/*/認定状態・総人口20**.csv")
    all_data = []
    for file in files:
        year = file[-8:-4]  # ファイル名から年を抽出
        df = pd.read_csv(file)
        df = df.drop_duplicates(subset=["住民コード_conv"])
        columns_to_keep = [
            "住民コード_conv",
            "自治会コード",
            "自治会コード名",
            "小学校区コード",
            "小学校区コード名",
            "生年月日_year",
            "認定状態",
        ]
        df = df[columns_to_keep]
        df["年"] = year
        df["年"] = df["年"].astype(int)
        df["行政区"] = df["自治会コード名"].str.extract("(.*区)")
        df["小学校区"] = df["小学校区コード名"].str.extract("(.*小)")
        df = df[df["生年月日_year"] < int(year) - 65]  # 65歳未満のデータを削除
        df["生年月日_year"] = df["生年月日_year"].astype(int)
        all_data.append(df)
    combined_data = pd.concat(all_data)
    return combined_data


data = load_and_process_files()


@callback(
    Output("certification_rate_graph", "figure"),
    [Input("target_select", "value"), Input("ward_select", "value")],
)
def update_graph(target_select, ward_select):
    fig = go.Figure()
    if not ward_select:
        ward_select = "全て"
    if ward_select is None or ward_select == "" or ward_select == "全て":
        filtered_data = data

        title = "全体の要介護認定率と後期高齢者率推移"
        process_data_and_add_trace(fig, filtered_data, "全体", include_elderly=True)
    else:
        if isinstance(ward_select, list):
            if len(ward_select) > 1:  # 複数選択の場合
                title = f"{target_select}別の要介護認定率推移"
                for ward in ward_select:
                    filtered_data = data[data[target_select] == ward]
                    process_data_and_add_trace(
                        fig, filtered_data, ward, include_elderly=False
                    )
            else:  # 単一選択の場合
                ward = ward_select[0]
                filtered_data = data[data[target_select] == ward]
                title = f"{ward}の要介護認定率と後期高齢者率推移"
                process_data_and_add_trace(
                    fig, filtered_data, ward, include_elderly=True
                )
        else:
            filtered_data = data[data[target_select] == ward_select]
            title = f"{target_select}別の要介護認定率と後期高齢者率推移"
            process_data_and_add_trace(
                fig, filtered_data, ward_select, include_elderly=True
            )

    fig.update_layout(
        title=title,
        xaxis_title="年",
        yaxis_title="割合 (%)",  # y軸のタイトルを変更
        yaxis=dict(tickformat=".2%"),  # y軸の値をパーセンテージ形式に設定
        barmode="overlay",
    )

    return fig


def process_data_and_add_trace(fig, filtered_data, label, include_elderly=False):
    grouped = (
        filtered_data.groupby("年", as_index=False)
        .apply(
            lambda x: pd.Series(
                {
                    "要介護認定率": (x["認定状態"] == "認定済み").mean(),
                    "後期高齢者率": (x["生年月日_year"] < x["年"] - 75).mean(),
                }
            )
        )
        .reset_index(drop=True)
    )

    # 要介護認定率の折れ線グラフ
    fig.add_trace(
        go.Scatter(
            x=grouped["年"],
            y=grouped["要介護認定率"],
            mode="lines+markers",
            name=f"{label}",
        )
    )

    # 後期高齢者率の縦棒グラフ
    if include_elderly:
        fig.add_trace(
            go.Bar(
                x=grouped["年"],
                y=grouped["後期高齢者率"],
                name=f"{label}の後期高齢者率",
                marker=dict(color="lightblue"),
                opacity=0.7,  # 透明度の設定
            )
        )


@callback(Output("ward_select", "options"), Input("target_select", "value"))
def update_menu(target_select):
    if target_select == "行政区":
        data["自治会コード_str"] = data["自治会コード"].astype(str)
        district_to_code = {
            district: code[:2]
            for district, code in zip(data["行政区"], data["自治会コード_str"])
        }
        sorted_districts = sorted(
            data["行政区"].unique(), key=lambda x: district_to_code.get(x, "")
        )
        options = [
            {"label": district, "value": district} for district in sorted_districts
        ]
    else:
        data["小学校区コード_str"] = data["小学校区コード"].astype(str)
        district_to_code = {
            district: code[:2]
            for district, code in zip(data["小学校区"], data["小学校区コード_str"])
        }
        sorted_districts = sorted(
            data["小学校区"].unique(), key=lambda x: district_to_code.get(x, "")
        )
        options = [
            {"label": district, "value": district} for district in sorted_districts
        ]
    return options
