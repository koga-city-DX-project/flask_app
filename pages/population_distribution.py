import base64
import math
import re

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, callback, dcc, html

df_path = "/usr/src/data/save/人口分布(国・福岡県・古賀市).csv"
contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("人口分布の推移(古賀市・福岡県・国)")],
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
                    id="aging_rate-graph",
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
                html.Div(id="population-zoom-range-store", style={"display": "none"}),
            ],
        ),
    ],
    style={"height": "100vh"},
)

settings = html.Div(
    children=[
        dbc.Row(
            dbc.Button(
                href="/select_populations",
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
                        html.P("比較方法", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-comparison-type-dropdown",
                            options=[
                                {"label": "人数", "value": "people"},
                                {"label": "年代別構成比", "value": "rate"},
                            ],
                            value="people",
                            className="setting_dropdown",
                            placeholder="人数で比較",
                        ),
                        html.P("年代", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-age-dropdown",
                            options=[
                                {"label": "10代", "value": "10代"},
                                {"label": "20代", "value": "20代"},
                                {"label": "30代", "value": "30代"},
                                {"label": "40代", "value": "40代"},
                                {"label": "50代", "value": "50代"},
                                {"label": "60代", "value": "60代"},
                                {"label": "70代", "value": "70代"},
                                {"label": "80代", "value": "80代"},
                                {"label": "90代", "value": "90代"},
                                {"label": "0歳～4歳", "value": "0歳～4歳"},
                                {"label": "5歳～9歳", "value": "5歳～9歳"},
                                {"label": "10歳～14歳", "value": "10歳～14歳"},
                                {"label": "15歳～19歳", "value": "15歳～19歳"},
                                {"label": "20歳～24歳", "value": "20歳～24歳"},
                                {"label": "25歳～29歳", "value": "25歳～29歳"},
                                {"label": "30歳～34歳", "value": "30歳～34歳"},
                                {"label": "35歳～39歳", "value": "35歳～39歳"},
                                {"label": "40歳～44歳", "value": "40歳～44歳"},
                                {"label": "45歳～49歳", "value": "45歳～49歳"},
                                {"label": "50歳～54歳", "value": "50歳～54歳"},
                                {"label": "55歳～59歳", "value": "55歳～59歳"},
                                {"label": "60歳～64歳", "value": "60歳～64歳"},
                                {"label": "65歳～69歳", "value": "65歳～69歳"},
                                {"label": "70歳～74歳", "value": "70歳～74歳"},
                                {"label": "75歳～79歳", "value": "75歳～79歳"},
                                {"label": "80歳～84歳", "value": "80歳～84歳"},
                                {"label": "85歳～89歳", "value": "85歳～89歳"},
                                {"label": "90歳～94歳", "value": "90歳～94歳"},
                                {"label": "95歳～99歳", "value": "95歳～99歳"},
                                {"label": "100歳～", "value": "100歳以上"},
                                {"label": "65歳～", "value": "65歳以上"},
                                {"label": "総数", "value": "総数"},
                            ],
                            value=[],
                            multi=True,
                            className="setting_dropdown",
                            placeholder="全年代を表示",
                        ),
                        html.P("性別", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-sex-type-dropdown",
                            options=[
                                {"label": "男性", "value": "男性"},
                                {"label": "女性", "value": "女性"},
                            ],
                            value=[],
                            multi=True,
                            className="setting_dropdown",
                            placeholder="男女合計数を表示",
                        ),
                        html.P("比較地域", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-area-dropdown",
                            options=[
                                {"label": "古賀市", "value": "古賀市"},
                                {"label": "福岡県", "value": "福岡県"},
                                {"label": "国", "value": "国"},
                            ],
                            value=["古賀市"],
                            placeholder="古賀市を表示",
                            multi=True,
                            className="setting_dropdown",
                        ),
                        dcc.Checklist(
                            id="population-aging-rate-checklist",
                            options=[{"label": "高齢者率を表示", "value": "show"}],
                            className="setting_dropdown option_P",
                        ),
                        dbc.Input(
                            id="population-file-name-input",
                            placeholder="ファイル名を入力",
                            type="text",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="population-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(id="population-modal-header"),
                                dbc.ModalBody(
                                    [
                                        html.Div(id="population-modal-text"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "ダウンロード",
                                                    id="population-download-confirm-button",
                                                    color="secondary",
                                                    className="me-2 bg-primary",
                                                ),
                                                dbc.Button(
                                                    "戻る",
                                                    id="population-cancel-button",
                                                    color="secondary",
                                                ),
                                            ],
                                            className="d-flex justify-content-center",
                                        ),
                                    ]
                                ),
                            ],
                            id="population-modal",
                            is_open=False,
                        ),
                        dcc.Download(id="download-population-distribution"),
                        dbc.Button(
                            "HTMLとしてグラフを出力",
                            id="export-population_distribution-graph-button",
                            className="text-white setting_button d-flex justify-content-center",
                            color="secondary",
                        ),
                        dcc.Download(id="download-population-distribution-html"),
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


@callback(
    [
        Output("aging_rate-graph", "figure"),
        Output("download-population-distribution-html", "data"),
    ],
    [
        Input("population-age-dropdown", "value"),
        Input("population-sex-type-dropdown", "value"),
        Input("population-area-dropdown", "value"),
        Input("population-aging-rate-checklist", "value"),
        Input("population-comparison-type-dropdown", "value"),
        Input("export-population_distribution-graph-button", "n_clicks"),
    ],
)
def update_population_graph(
    ages, sexes, areas, aging_rate_visibility, comparison_type, export_html
):
    df = pd.read_csv(df_path)
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = "No clicks yet"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    widths = {"古賀市": 1, "福岡県": 2, "国": 3}
    symbols = {"古賀市": "circle", "福岡県": "square", "国": "diamond"}
    line_styles = {"男性": "solid", "女性": "dot", "男女計": "solid"}
    if not ages:
        ages = ["総数"]
    if not sexes:
        sexes = ["男女計"]
    if not areas:
        areas = ["古賀市"]

    if not isinstance(ages, list):
        ages = [ages]
    if not isinstance(sexes, list):
        sexes = [sexes]
    if not isinstance(areas, list):
        areas = [areas]
    title = f"人口分布の推移(地域: {', '.join(areas)}  性別: {', '.join(sexes)}  年代: {', '.join(ages)})"

    df_filtered = df[df["地域"].isin(areas) & df["性別"].isin(sexes)]

    fig = go.Figure()
    for area in areas:
        symbol = symbols[area]
        for sex in sexes:
            line_style = line_styles[sex]
            line_width = widths[area]
            df_area_sex_age = df_filtered[
                (df_filtered["地域"] == area) & (df_filtered["性別"] == sex)
            ]
            if len(areas) == 1 and len(ages) == 1 and comparison_type == "people":
                for age in ages:
                    y_data, y_title, y_tickformat = y_settings(
                        comparison_type, df_area_sex_age, age
                    )
                    if len(sexes) == 2:
                        fig.add_trace(
                            go.Bar(
                                x=df_area_sex_age["年度"],
                                y=y_data,
                                name=f"{area} {sex} {age}",
                                offsetgroup=sex,
                                opacity=0.7,
                            )
                        )
                    else:
                        fig.add_trace(
                            go.Bar(
                                x=df_area_sex_age["年度"],
                                y=y_data,
                                name=f"{area} {sex} {age}",
                                opacity=0.7,
                            )
                        )
            else:
                for age in ages:
                    y_data, y_title, y_tickformat = y_settings(
                        comparison_type, df_area_sex_age, age
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_area_sex_age["年度"],
                            y=y_data,
                            mode="lines+markers",
                            name=f"{area} {sex} {age}",
                            line=dict(width=line_width, dash=line_style),
                            marker=dict(symbol=symbol, size=12),
                        )
                    )

            if aging_rate_visibility == ["show"]:
                df_area = df_filtered[
                    (df_filtered["地域"] == area) & (df_filtered["性別"] == sex)
                ]
                fig.add_trace(
                    go.Scatter(
                        x=df_area["年度"],
                        y=df_area["高齢化率"],
                        mode="lines",
                        name=f"{area} 高齢化率({sex})",
                        yaxis="y2",
                        line=dict(width=2.5, dash="solid"),
                        showlegend=True,
                    )
                )

    fig.update_layout(
        title=title,
        title_font_size=24,
        xaxis=dict(title="年度", title_font=dict(size=20)),
        yaxis=dict(
            title=y_title,
            title_font=dict(size=20),
            tickformat=y_tickformat,
        ),
        yaxis2=dict(
            title="高齢化率",
            title_font=dict(size=20),
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, 1],
            tickformat=".2%",
        ),
        legend=dict(
            x=1.05,
            y=1,
        ),
        barmode="group",
    )

    if trigger_id == "export-population_distribution-graph-button":
        html_bytes = fig.to_html().encode("utf-8")
        return fig, dcc.send_bytes(
            html_bytes, filename="population_distribution_graph.html"
        )
    return fig, None


@callback(
    [
        Output("population-modal", "is_open"),
        Output("population-modal-header", "children"),
        Output("population-modal-text", "children"),
    ],
    [
        Input("population-download-button", "n_clicks"),
        Input("population-cancel-button", "n_clicks"),
        Input("population-download-confirm-button", "n_clicks"),
    ],
    [
        State("population-modal", "is_open"),
        State("population-sex-type-dropdown", "value"),
        State("population-area-dropdown", "value"),
        State("population-aging-rate-checklist", "value"),
        State("population-file-name-input", "value"),
        State("population-zoom-range-store", "children"),
    ],
)
def toggle_modal(
    n_open,
    n_cancel,
    n_download,
    is_open,
    sexes,
    areas,
    aging_rate_visibility,
    file_name,
    zoom_range,
):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    sexes_text = ", ".join(sexes) if sexes else "男性,女性,男女計"
    file_name = re.sub(r"[\s　]+", "", file_name) if file_name else ""
    if file_name is None or file_name == "":
        file_name = "population.csv(※ファイル名未入力時)"
    else:
        file_name = f"{file_name}.csv"
    areas_text = ", ".join(areas) if areas else "古賀市,福岡県,国"
    aging_text = "表示" if aging_rate_visibility else "非表示"
    if zoom_range:
        start_year = math.ceil(zoom_range[0])
        end_year = math.floor(zoom_range[1])
        year_text = f"{start_year}年 - {end_year}年"
    else:
        year_text = "すべての年度"
    modal_body_text = [
        html.Div("ファイル名"),
        html.P(file_name),
        html.Div("選択性別"),
        html.P(sexes_text),
        html.Div(
            [
                html.Div("選択地域"),
                html.P(areas_text),
            ]
        ),
        html.Div("高齢化率"),
        html.P(aging_text),
        html.Div("選択年度"),
        html.P(year_text),
    ]

    if button_id == "population-download-button":
        return True, "ファイルの出力", modal_body_text
    elif button_id in [
        "population-cancel-button",
        "population-download-confirm-button",
    ]:
        return False, "", modal_body_text
    return is_open, "", modal_body_text


@callback(
    Output("download-population-distribution", "data"),
    [Input("population-download-confirm-button", "n_clicks")],
    [
        State("population-sex-type-dropdown", "value"),
        State("population-area-dropdown", "value"),
        State("population-file-name-input", "value"),
        State("population-zoom-range-store", "children"),
        State("population-aging-rate-checklist", "value"),
    ],
    prevent_initial_call=True,
)
def download_file(n_clicks, sexes, areas, file_name, zoom_range, aging_rate_visibility):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "population-download-confirm-button":
        filepath = "/usr/src/data/save/人口分布(国・福岡県・古賀市).csv"
        df = pd.read_csv(filepath)
        df_filtered = filter_df(df, sexes, areas, zoom_range, aging_rate_visibility)
        if file_name is None or file_name == "":
            file_name = "population"
        df_filtered = df_filtered.to_csv(index=False)
        b64 = base64.b64encode(df_filtered.encode("CP932")).decode("CP932")
        return dict(content=b64, filename=f"{file_name}.csv", base64=True)


@callback(
    Output("population-zoom-range-store", "children"),
    [
        Input("aging_rate-graph", "relayoutData"),
        Input("population-comparison-type-dropdown", "value"),
        Input("population-age-dropdown", "value"),
        Input("population-sex-type-dropdown", "value"),
        Input("population-area-dropdown", "value"),
        Input("population-aging-rate-checklist", "value"),
    ],
)
def update_zoom_range_store(
    relayoutData, comparison_type, age, sex, area, aging_rate_visibility
):
    if not relayoutData:
        return dash.no_update
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if (
        button_id == "population-comparison-type-dropdown"
        or button_id == "population-age-dropdown"
        or button_id == "population-sex-type-dropdown"
        or button_id == "population-area-dropdown"
        or button_id == "population-aging-rate-checklist"
    ):
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


def filter_df(df, sexes, areas, zoom_range, aging_rate_visibility):
    if areas is None or areas == []:
        areas = ["古賀市", "福岡県", "国"]
    if sexes is None or sexes == []:
        sexes = ["男性", "女性", "男女計"]

    df_filtered = df[df["地域"].isin(areas)]
    df_filtered = df_filtered[df_filtered["性別"].isin(sexes)]
    if aging_rate_visibility != ["show"]:
        df_filtered = df_filtered.drop(columns=["高齢化率"])
    if zoom_range:
        df_filtered = df_filtered[
            (df_filtered["年度"] >= float(zoom_range[0]))
            & (df_filtered["年度"] <= float(zoom_range[1]))
        ]
    return df_filtered


def y_settings(comparison, df, age):
    if comparison == "rate":
        y_data = df[age] / df["総数"]
        y_title = "割合"
        y_tickformat = ".2%"
    else:
        y_data = df[age]
        y_title = "人数"
        y_tickformat = None
    return y_data, y_title, y_tickformat
