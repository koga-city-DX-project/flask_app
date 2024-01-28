import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

df_path = "/usr/src/data/save/介護認定管理.csv"
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
                        html.P("年代", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-age-dropdown",
                            options=[],
                            className="setting_dropdown",
                        ),
                        html.P("性別", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="sex-type-dropdown",
                            options=[
                                {"label": "男性", "value": "men"},
                                {"label": "女性", "value": "women"},
                                {"label": "すべて", "value": "all"},
                            ],
                            className="setting_dropdown",
                        ),
                        html.P("比較地域", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="graph-type-dropdown",
                            options=[
                                {"label": "古賀市", "value": "koga"},
                                {"label": "福岡県", "value": "hukuoka"},
                                {"label": "国", "value": "all"},
                            ],
                            className="setting_dropdown",
                        ),
                        html.P("高齢化率", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="graph-type-dropdown",
                            options=[
                                {"label": "表示", "value": "show"},
                                {"label": "非表示", "value": "hidden"},
                            ],
                            className="setting_dropdown",
                        ),
                        dbc.Button(
                            id="care-lebel-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dcc.Download(id="download-dataframe-csv"),
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