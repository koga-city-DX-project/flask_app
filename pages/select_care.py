import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import html

contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("メインメニュー")],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            html.P(
                "ダッシュボード選択",
                style={
                    "margin-top": "8px",
                    "margin-bottom": "0",
                    "font-size": "1.3em",
                },
                className="font-weight-bold",
            ),
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "介護度データ出力・分析",
                        href="/primary_care",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link=True,
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "font-size": "1.3em"},
                    ),
                    width=6,
                    className="d-flex align-items-stretch",
                ),
                dbc.Col(
                    dbc.Button(
                        "○○ページ",
                        href="#",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link=True,
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "font-size": "1.3em"},
                    ),
                    width=6,
                    className="d-flex align-items-stretch",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "○○ページ",
                        href="#",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link=True,
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "font-size": "1.3em"},
                    ),
                    width=6,
                    className="d-flex align-items-stretch",
                ),
                dbc.Col(
                    dbc.Button(
                        "○○ページ",
                        href="#",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link=True,
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "font-size": "1.3em"},
                    ),
                    width=6,
                    className="d-flex align-items-stretch",
                ),
            ],
            style={"height": "100vh"},
        ),
    ],
)

settings = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H6(
                                "分析ツール",
                            ),
                        ],
                        className="align-items-center",
                    ),
                    className="col-10",
                ),
            ],
            className="bg-primary text-white font-italic justify-content-start topMenu",
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        html.P(
                            "カテゴリー別",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "0",
                                "font-size": "1.3em",
                            },
                            className="font-weight-bold",
                        ),
                        html.Hr(),
                        dbc.Button(
                            href="/",
                            children="介護",
                            className=" text-white setting_button",
                            external_link=True,
                            color="secondary",
                            disabled=True,
                        ),
                        dbc.Button(
                            href="/tax",
                            children="税務",
                            className=" text-white setting_button",
                            external_link=True,
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="農地",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="子ども",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="○○に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="○○に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "25vh", "margin-left": "1px"},
        ),
    ]
)

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    settings,
                    className="bg-primary bg-opacity-25 bg-gradient",
                    width=2,
                ),
                dbc.Col(
                    contents,
                    className="bg-light bg-gradient",
                    width=10,
                ),
            ]
        )
    ]
)
