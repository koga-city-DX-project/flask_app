import os
from glob import glob

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback, dcc, html

contents = html.Div(
    [
        html.Div(id="trigger", style={"display": "none"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("介護度データ出力・分析")],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu ",
        ),
        dbc.Row(
            [
                html.Div("a"),
            ],
        ),
        dbc.Row(
            [
                dcc.Graph(id="certification_rate_graph"),
                dcc.Graph(id="care_level_distribution_graph"),
            ]
        ),
        dbc.Row(
            [
                html.Div("a"),
            ],
            style={"height": "100vh"},
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
                external_link=True,
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
                                "margin-top": "8px",
                                "margin-bottom": "0",
                                "font-size": "1.3em",
                            },
                            className="font-weight-bold",
                        ),
                        html.Hr(),
                        html.P(
                            "表示期間",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="duration_select",
                            options=[
                                {"label": "年ごと", "value": "Y"},
                                {"label": "月ごと", "value": "M"},
                            ],
                            value="Y",
                            className="setting_dropdown",
                            placeholder="表示期間を選択",
                        ),
                        html.P(
                            "行政区別",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(  ##!!!
                            id="gov_select",
                            options=[
                                {"label": "指定なし", "value": "city0"},
                            ],
                            value="city0",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="行政区別にみる",
                        ),
                        html.P(
                            "介護度別",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(  ##!!!
                            id="care_level_select",
                            options=[
                                {"label": "指定なし", "value": "k0"},
                            ],
                            value="k0",
                            className="setting_dropdown",
                            placeholder="介護度別にみる",
                        ),
                        dbc.Button(
                            href="#",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link=True,
                            color="secondary",
                        ),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "35vh", "margin-left": "1px"},
        ),
    ]
)

settings.children.append(
    dbc.Row(
        dcc.Dropdown(
            id="year_select",
            className="setting_dropdown",
            placeholder="西暦を選択",
        ),
        style={"display": "none"},  # 最初は非表示
        id="year_select_row",
    )
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


def load_and_process_data():
    file_paths = glob("/usr/src/data/*/認定率*.csv")
    data_frames = []

    for fp in file_paths:
        try:
            df = pd.read_csv(fp)
            if not df.empty:
                # ここで新しい列 '行政区' を作成
                df["行政区"] = df["自治会コード名"].str.extract("(.*?)区")
                data_frames.append(df)
        except Exception as e:
            print(f"Error reading {fp}: {e}")

    if not data_frames:
        print("No valid CSV files found to concatenate.")
        return pd.DataFrame()

    data = pd.concat(data_frames)
    return data


# データ処理のヘルパー関数
def calculate_certification_rate(data, duration, gov_select, care_level_select):
    gov_select = [gov_select] if isinstance(gov_select, str) else gov_select
    care_level_select = (
        [care_level_select] if isinstance(care_level_select, str) else care_level_select
    )
    # データフィルタリング
    if gov_select != ["指定なし"]:
        data = data[data["行政区"].isin(gov_select)]
    if care_level_select != ["指定なし"]:
        data = data[data["介護度"].isin(care_level_select)]

    # 認定率の計算
    data["認定日"] = pd.to_datetime(data["認定日"])

    if duration == "年ごと":
        data["年"] = data["認定日"].dt.year
        group_by_column = "年"
    else:  # "月ごと"
        data["年月"] = data["認定日"].dt.to_period("M").dt.to_timestamp()
        group_by_column = "年月"

    certification_rate = (
        data.groupby(group_by_column)["認定"]
        .apply(lambda x: (x == "済").sum() / len(x))
        .reset_index(name="認定率")
    )
    return certification_rate, group_by_column


def calculate_care_level_distribution(data, gov_select):
    if len(gov_select) == 1 and gov_select[0] != "指定なし":
        data = data[data["行政区"] == gov_select[0]]
        care_level_distribution = data["介護度"].value_counts(normalize=True).reset_index()
        return care_level_distribution
    return pd.DataFrame()


@callback(
    [
        Output("certification_rate_graph", "figure"),
        Output("care_level_distribution_graph", "figure"),
        Output("care_level_distribution_graph", "style"),
        Output("gov_select", "options"),
        Output("care_level_select", "options"),
    ],
    [
        Input("duration_select", "value"),
        Input("gov_select", "value"),
        Input("care_level_select", "value"),
    ],
)
def update_graphs(duration, gov_select, care_level_select):
    data = load_and_process_data()
    filtered_data = data.copy()

    # 認定率の計算
    certification_rate_df, group_by_column = calculate_certification_rate(
        filtered_data, duration, gov_select, care_level_select
    )

    # 折れ線グラフの作成
    certification_rate_figure = px.line(
        certification_rate_df,
        x=group_by_column,
        y="認定率",
        title="認定率の推移",
    )
    # 介護度別の積み上げ棒グラフの作成（行政区別が1つのみ選択された場合）
    care_level_distribution_figure = {}
    care_level_graph_style = {"display": "none"}
    if len(gov_select) == 1:
        care_level_distribution_df = calculate_care_level_distribution(
            filtered_data, gov_select
        )
        care_level_distribution_figure = px.bar(
            care_level_distribution_df,
            x="index",
            y="介護度",
            title=f"{gov_select[0]}の介護度別割合",
        )
        care_level_graph_style = {"display": "block"}
    unique_gov = sorted(
        [{"label": i, "value": i} for i in data["行政区"].unique() if pd.notna(i)],
        key=lambda x: x["label"],
    )
    unique_care_levels = sorted(
        [{"label": i, "value": i} for i in data["介護度"].unique() if pd.notna(i)],
        key=lambda x: x["label"],
    )
    return (
        certification_rate_figure,
        care_level_distribution_figure,
        care_level_graph_style,
        unique_gov,
        unique_care_levels,
    )
