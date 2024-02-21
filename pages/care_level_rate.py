import base64
import math
import os
import re

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, callback, dcc, html

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
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToAdd": [
                            "pan2d",
                            "autoScale2d",
                        ],
                        "modeBarButtonsToRemove": [
                            "zoomIn2d",
                            "zoomOut2d",
                            "select2d",
                            "lasso2d",
                            "toggleSpikelines",
                            "hoverClosestCartesian",
                            "hoverCompareCartesian",
                        ],
                    },
                ),
                html.Div(id="care-level-zoom-range-store", style={"display": "none"}),
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
                        html.P("グラフの種類", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="care-level-graph-type-dropdown",
                            options=[
                                {"label": "折れ線グラフ", "value": "line"},
                                {"label": "縦積み棒グラフ", "value": "stacked_bar"},
                            ],
                            value="line",
                            className="setting_dropdown",
                        ),
                        dbc.Input(
                            id="care-level-file-name-input",
                            placeholder="ファイル名を入力",
                            type="text",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="care-level-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(id="care-level-modal-header"),
                                dbc.ModalBody(
                                    [
                                        html.Div(id="care-level-modal-text"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "ダウンロード",
                                                    id="care-level-download-confirm-button",
                                                    color="secondary",
                                                    className="me-2 bg-primary",
                                                ),
                                                dbc.Button(
                                                    "戻る",
                                                    id="care-level-cancel-button",
                                                    color="secondary",
                                                ),
                                            ],
                                            className="d-flex justify-content-center",
                                        ),
                                    ]
                                ),
                            ],
                            id="care-level-modal",
                            is_open=False,
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
            elderly_data = elderly_data[elderly_data["二次判定要介護度名"] != "非該当"]
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
                elderly_data.groupby("二次判定要介護度名")
                .size()
                .reset_index(name="合計")
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

    if len(selected_care_levels) != 0:
        df = df[df["二次判定要介護度名"].isin(selected_care_levels)]

    fig = go.Figure()

    if selected_graph_type == "line":
        care_levels = (
            df["二次判定要介護度名"].unique()
            if not selected_care_levels
            else selected_care_levels
        )
        for care_level in care_levels:
            level_df = df[df["二次判定要介護度名"] == care_level]
            if len(care_levels) <= 2:
                fig.add_trace(
                    go.Bar(
                        x=level_df["Year"],
                        y=level_df["合計"],
                        yaxis="y2",
                        name=f"{care_level}総人数",
                        marker=dict(
                            color=color_map.get(care_level, "black"),
                            opacity=0.6,
                        ),
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=level_df["Year"],
                    y=level_df["割合"],
                    mode="lines",
                    name=care_level,
                    line=dict(color=color_map.get(care_level, "black")),
                )
            )
    elif selected_graph_type == "stacked_bar":
        data = []
        for care_level in df["二次判定要介護度名"].unique():
            level_df = df[df["二次判定要介護度名"] == care_level]
            data.append(
                go.Bar(
                    x=level_df["Year"],
                    y=level_df["割合"],
                    name=care_level,
                    marker=dict(
                        color=color_map.get(care_level, "black"),
                        opacity=0.7,
                    ),
                )
            )
        fig = go.Figure(data=data)
        fig.update_layout(barmode="stack")

    fig.update_layout(
        title="選択された要介護度の年次推移",
        title_font=dict(size=24),
        xaxis_title="年度",
        xaxis_title_font=dict(size=20),
        yaxis_title="割合",
        yaxis_title_font=dict(size=20),
        yaxis2=dict(
            title="人数",
            title_font=dict(size=20),
            overlaying="y",
            side="right",
            tickformat=",",
        ),
        legend_title="介護度名",
        xaxis={"type": "category"},
    )

    return fig


@callback(
    [
        Output("care-level-modal", "is_open"),
        Output("care-level-modal-header", "children"),
        Output("care-level-modal-text", "children"),
    ],
    [
        Input("care-level-download-button", "n_clicks"),
        Input("care-level-cancel-button", "n_clicks"),
        Input("care-level-download-confirm-button", "n_clicks"),
    ],
    [
        State("care-level-modal", "is_open"),
        State("care-level-rate-dropdown", "value"),
        State("care-level-file-name-input", "value"),
        State("care-level-zoom-range-store", "children"),
    ],
)
def toggle_modal(
    n_open,
    n_cancel,
    n_download,
    is_open,
    levels,
    file_name,
    zoom_range,
):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    file_name = re.sub(r"[\s　]+", "", file_name) if file_name else ""
    if file_name is None or file_name == "":
        file_name = "care_level_rate.csv(※ファイル名未入力時)"
    else:
        file_name = f"{file_name}.csv"

    levels_text = ", ".join(levels) if levels else "すべての介護度"
    if zoom_range:
        start_year = math.ceil(zoom_range[0])
        end_year = math.floor(zoom_range[1])
        year_text = f"{start_year}年 - {end_year}年"
    else:
        year_text = "すべての年度"
    modal_body_text = [
        html.Div("ファイル名"),
        html.P(file_name),
        html.Div(
            [
                html.Div("選択した介護度"),
                html.P(levels_text),
            ]
        ),
        html.Div("選択年度"),
        html.P(year_text),
    ]

    if button_id == "care-level-download-button":
        return True, "ファイルの出力", modal_body_text
    elif button_id in [
        "care-level-cancel-button",
        "care-level-download-confirm-button",
    ]:
        return False, "", modal_body_text
    return is_open, "", modal_body_text


@callback(
    Output("care-level-zoom-range-store", "children"),
    [
        Input("care-level-graph", "relayoutData"),
        Input("care-level-graph-type-dropdown", "value"),
    ],
)
def update_zoom_range_store(relayoutData, graph_type):
    if not relayoutData:
        return dash.no_update
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "care-level-graph-type-dropdown":
        return None
    if "xaxis.autorange" in relayoutData or "yaxis.autorange" in relayoutData:
        return None
    if ("yaxis.range[0]" in relayoutData or "yaxis.range[1]" in relayoutData) and (
        "xaxis.range[0]" not in relayoutData or "xaxis.range[1]" not in relayoutData
    ):
        return dash.no_update
    if (
        relayoutData
        and "xaxis.range[0]" in relayoutData
        and "xaxis.range[1]" in relayoutData
    ):
        return [relayoutData["xaxis.range[0]"], relayoutData["xaxis.range[1]"]]
    return dash.no_update


@callback(
    Output("download-care-level-rate", "data"),
    [Input("care-level-download-confirm-button", "n_clicks")],
    [
        State("care-level-rate-dropdown", "value"),
        State("care-level-file-name-input", "value"),
        State("care-level-zoom-range-store", "children"),
    ],
    prevent_initial_call=True,
)
def download_file(n_clicks, care_level, file_name, zoom_range):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "care-level-download-confirm-button":
        filepath = "/usr/src/data/save/認定者数0124.csv"
        df = pd.read_csv(filepath)
        df_filtered = filter_df_by_care_level(df, care_level)

        if zoom_range:
            df_filtered = df_filtered[
                (df_filtered["年度"] >= float(zoom_range[0]))
                & (df_filtered["年度"] <= float(zoom_range[1]))
            ]
        if file_name is None or file_name == "":
            file_name = "care_level_rate"
        df_filtered = df_filtered[["Year", "二次判定要介護度名", "合計", "割合"]]
        care_order = [
            "要介護５",
            "要介護４",
            "要介護３",
            "要介護２",
            "要介護１",
            "要支援２",
            "要支援１",
            "経過的要介護",
        ]
        df_filtered["二次判定要介護度名"] = pd.Categorical(
            df_filtered["二次判定要介護度名"], categories=care_order, ordered=True
        )
        df_filtered = df_filtered.sort_values(by=["Year", "二次判定要介護度名"])
        df_filtered = df_filtered.to_csv(index=False)
        b64 = base64.b64encode(df_filtered.encode("CP932")).decode("CP932")
        return dict(content=b64, filename=f"{file_name}.csv", base64=True)


def filter_df_by_care_level(df, care_level):
    if care_level:
        df = df[df["二次判定要介護度名"].isin(care_level)]
    return df
