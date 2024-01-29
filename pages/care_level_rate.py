import os
import re

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

data_directory = "/usr/src/data/save/"
file_pattern = re.compile(r"認定状態・総人口20(\d{2}).csv")

column_types = {
    "異動ＳＥＱ": int,
    "増異動日": int,
    "増事由コード名": str,
    "減異動日": int,
    "減事由コード名": "Int8",
    "最新異動日": int,
    "最新異動事由コード名": str,
    "性別": int,
    "性別名": str,
    "死亡日": str,
    "続柄": str,
    "続柄名": str,
    "住民となった異動日": int,
    "自治会コード": int,
    "自治会コード名": str,
    "小学校区コード": int,
    "小学校区コード名": str,
    "住民コード_conv": int,
    "世帯コード_conv": int,
    "生年月日_conv": str,
    "住所_conv": str,
    "生年月日_year": int,
    "要介護認定申請日": str,
    "二次判定要介護度": "Int64",
    "二次判定要介護度名": str,
    "要介護認定日": str,
    "認定開始日": str,
    "認定終了日": str,
    "認定状態": str,
}

contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("認定度(要介護度)ごとの率の推移")],
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
                    id="care-level-graph",
                    style={"height": "80vh"},
                )
            ],
        ),
    ],
    style={"height": "100vh"},
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
                            "介護度別",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="care-level-rate-dropdown",
                            options=[
                                {"label": "要介護5", "value": "要介護５"},
                                {"label": "要介護4", "value": "要介護４"},
                                {"label": "要介護3", "value": "要介護３"},
                                {"label": "要介護2", "value": "要介護２"},
                                {"label": "要介護1", "value": "要介護１"},
                                {"label": "要支援2", "value": "要支援２"},
                                {"label": "要支援1", "value": "要支援１"},
                            ],
                            value=[],
                            className="setting_dropdown",
                            placeholder="すべての介護度を表示",
                            multi=True,
                        ),
                        html.P("グラフの種類", className="font-weight-bold"),
                        dcc.Dropdown(
                            id="care-level-graph-type-dropdown",
                            options=[
                                {"label": "折れ線グラフ", "value": "line"},
                                {"label": "縦積み棒グラフ", "value": "stacked_bar"},
                            ],
                            value="line",
                            className="setting_dropdown",
                        ),
                        dbc.Button(
                            id="care-lebel-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dcc.Download(id="download-care-level-rate"),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "20vh", "marginLeft": "1px"},
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


def process_data(data_directory, file_pattern):
    aging_data = pd.DataFrame()
    for file_name in os.listdir(data_directory):
        match = file_pattern.match(file_name)
        if match:
            year = int("20" + match.group(1))
            file_path = os.path.join(data_directory, file_name)
            df = pd.read_csv(file_path, encoding="utf-8", dtype=column_types)
            df = df[df["認定状態"] == "認定済み"]
            df["年齢"] = year - df["生年月日_year"] + 1
            elderly_data = df[df["年齢"] >= 65]
            elderly_data = elderly_data[
                [
                    "要介護認定申請日",
                    "二次判定要介護度名",
                    "住民コード_conv",
                    "認定開始日",
                    "認定終了日",
                ]
            ]
            elderly_data["Year"] = year
            counts_by_care_level = (
                elderly_data.groupby("二次判定要介護度名").size().reset_index(name="合計")
            )
            counts_by_care_level["Year"] = year
            total_by_year = counts_by_care_level["合計"].sum()
            counts_by_care_level["割合"] = (
                counts_by_care_level["合計"] / total_by_year * 100
            )

            aging_data = pd.concat(
                [aging_data, counts_by_care_level], ignore_index=True
            )
    aging_data = aging_data.sort_values(by="Year")

    filepath = "/usr/src/data/save/認定者数0124.csv"
    aging_data.to_csv(filepath, index=False)


color_map = {
    "要支援１": "blue",
    "要支援２": "#5bb8eb",
    "要介護１": "green",
    "要介護２": "#0fd614",
    "要介護３": "#ffbb00",
    "要介護４": "#ff6600",
    "要介護５": "#ff0000",
    "非該当": "gray",
    "再調査": "gray",
    "経過的要介護": "gray",
}


@callback(
    Output("care-level-graph", "figure"),
    [
        Input("care-level-rate-dropdown", "value"),
        Input("care-level-graph-type-dropdown", "value"),
    ],
)
def update_graph(selected_care_levels, selected_graph_type):
    # process_data(data_directory, file_pattern)
    filepath = "/usr/src/data/save/認定者数0124.csv"
    df = pd.read_csv(filepath, encoding="utf-8")

    # 選択された介護度に基づいてデータをフィルタリング
    if len(selected_care_levels) != 0:
        df = df[df["二次判定要介護度名"].isin(selected_care_levels)]

    # グラフの初期化
    fig = go.Figure()

    # グラフタイプに基づいてグラフを描画
    if selected_graph_type == "line":
        care_levels = (
            df["二次判定要介護度名"].unique()
            if not selected_care_levels
            else selected_care_levels
        )
        for care_level in care_levels:
            level_df = df[df["二次判定要介護度名"] == care_level]
            fig.add_trace(
                go.Scatter(
                    x=level_df["Year"],
                    y=level_df["割合"],
                    mode="lines",
                    name=care_level,
                    line=dict(
                        color=color_map.get(care_level, "black")
                    ),  # カラーマップから色を設定、デフォルトは黒
                )
            )
            if len(care_levels) == 1:
                fig.add_trace(
                    go.Bar(
                        x=level_df["Year"],
                        y=level_df["合計"],
                        yaxis="y2",
                        name=f"{care_level}総人数",
                        marker=dict(
                            color=color_map.get(care_level, "black"),
                            opacity=0.4,
                        ),
                    )
                )
    elif selected_graph_type == "stacked_bar":
        # 積み上げ棒グラフのデータを準備
        data = []
        for care_level in df["二次判定要介護度名"].unique():
            level_df = df[df["二次判定要介護度名"] == care_level]
            data.append(
                go.Bar(
                    x=level_df["Year"],
                    y=level_df["割合"],
                    name=care_level,
                    marker=dict(
                        color=color_map.get(care_level, "black")
                    ),  # カラーマップから色を設定、デフォルトは黒
                )
            )
        fig = go.Figure(data=data)
        fig.update_layout(barmode="stack")

    # グラフのレイアウト設定
    fig.update_layout(
        title="選択された要介護度の年次推移",
        xaxis_title="年度",
        yaxis_title="割合",
        yaxis2=dict(
            title="人数",
            title_font=dict(size=20),
            overlaying="y",
            side="right",
            tickformat=",",
        ),
        legend_title="介護度名",
        xaxis={"type": "category"},  # X軸をカテゴリ型に設定
    )

    return fig


@callback(
    Output("download-care-level-rate", "data"),
    [Input("care-lebel-download-button", "n_clicks")],
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    return dcc.send_file("/usr/src/data/save/介護認定管理.csv")
