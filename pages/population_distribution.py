import colorsys

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
                                {"label": "年代別割合", "value": "rate"},
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
                                {"label": "男女計", "value": "男女計"},
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
                            value=["古賀市", "福岡県", "国"],
                            placeholder="すべての地域を表示",
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
                            id="population-file-download-button",
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
    Output("aging_rate-graph", "figure"),
    [
        Input("population-age-dropdown", "value"),
        Input("population-sex-type-dropdown", "value"),
        Input("population-area-dropdown", "value"),
        Input("population-aging-rate-checklist", "value"),
        Input("population-comparison-type-dropdown", "value"),
    ],
)
def update_population_graph(ages, sexes, areas, aging_rate_visibility, comparison_type):
    df = pd.read_csv(df_path)
    widths = {"古賀市": 1, "福岡県": 2, "国": 3}
    symbols = {"古賀市": "circle", "福岡県": "square", "国": "diamond"}
    line_styles = {"男性": "solid", "女性": "dot", "男女計": "solid"}
    if not ages:
        ages = ["総数"]
    if not sexes:
        sexes = ["男女計"]
    if not areas:
        areas = ["古賀市", "福岡県", "国"]

    if not isinstance(ages, list):
        ages = [ages]
    if not isinstance(sexes, list):
        sexes = [sexes]
    if not isinstance(areas, list):
        areas = [areas]

    df_filtered = df[df["地域"].isin(areas) & df["性別"].isin(sexes)]

    fig = go.Figure()
    for area in areas:
        symbol = symbols[area]
        for sex in sexes:
            line_style = line_styles[sex]
            for age in ages:
                line_width = widths[area]
                df_area_sex_age = df_filtered[
                    (df_filtered["地域"] == area) & (df_filtered["性別"] == sex)
                ]
                if comparison_type == "rate":
                    y_data = df_area_sex_age[age] / df_area_sex_age["総数"]
                    y_title = "割合"
                    y_tickformat = ".2%"
                else:
                    y_data = df_area_sex_age[age]
                    y_title = "人数"
                    y_tickformat = None
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
        title="人口分布の推移",
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
    )

    return fig


@callback(
    Output("download-population-distribution", "data"),
    [Input("care-lebel-download-button", "n_clicks")],
    [
        State("population-age-dropdown", "value"),
        State("population-sex-type-dropdown", "value"),
        State("population-area-dropdown", "value"),
        State("population-comparison-type-dropdown", "value"),
    ],
)
def generate_csv(
    n_clicks, selected_ages, selected_sexes, selected_areas, comparison_type
):
    if n_clicks is None:
        return dash.no_update
    return 0
