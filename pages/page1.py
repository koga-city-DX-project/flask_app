import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

df = pd.read_csv("data/data_sample.csv")
vars_cat = [var for var in df.columns if var.startswith("cat")]
vars_cont = [var for var in df.columns if var.startswith("cont")]


sidebarToggleBtn = dbc.Button(
    children=[html.I(className="fas fa-bars", style={"color": "#c2c7d0"})],
    color="dark",
    className="opacity-50",
    id="sidebar-button",
)


contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H6(
                                    "タイトルタイトル",
                                )
                            ],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu ",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(id="bar-title", className="font-weight-bold"),
                            dcc.Graph(id="bar-chart", className="bg-light"),
                        ]
                    ),
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.P(id="dist-title", className="font-weight-bold"),
                            dcc.Graph(id="dist-chart", className="bg-light"),
                        ]
                    ),
                    width=6,
                ),
            ],
            style={
                "margin": "2vh 1vw 1vh 1vw",
            },
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        html.P(
                            "ヒートマップ",
                            className="font-weight-bold",
                        ),
                        dcc.Graph(id="corr-chart", className="bg-light"),
                    ]
                )
            ],
            style={"margin": "8px", "height": "100vh"},
        ),
    ],
)

settings = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(sidebarToggleBtn, className="col-2", id="setting_Col"),
                dbc.Col(
                    html.Div(
                        [
                            html.H6(
                                "Settings",
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
                            "カテゴリー変数",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="my-cat-picker",
                            multi=False,
                            value="cat0",
                            options=[{"label": x, "value": x} for x in vars_cat],
                            style={"width": "95%"},
                        ),
                        html.P(
                            "連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="my-cont-picker",
                            multi=False,
                            value="cont0",
                            options=[{"label": x, "value": x} for x in vars_cont],
                            style={"width": "95%"},
                        ),
                        html.P(
                            "相関行列の連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="my-corr-picker",
                            multi=True,
                            value=vars_cont + ["target"],
                            options=[
                                {"label": x, "value": x} for x in vars_cont + ["target"]
                            ],
                            style={"width": "95%"},
                        ),
                        html.Button(
                            id="my-button",
                            n_clicks=0,
                            children="設定変更",
                            style={"margin-top": "16px"},
                            className="bg-dark text-white",
                        ),
                        html.Hr(),
                    ]
                )
            ],
            style={"height": "50vh", "margin": "8px"},
        ),
    ]
)

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [settings],
                    className="bg-light",
                    width=2,
                ),
                dbc.Col(
                    contents,
                    style={
                        "transition": "margin-left 0.3s ease-in-out",
                    },
                    width=10,
                ),
            ]
        )
    ]
)
