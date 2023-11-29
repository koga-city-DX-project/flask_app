import dash_bootstrap_components as dbc
from dash import dcc, html

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
                                    "データ加工・編集",
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
            html.Div(
                [
                    html.P(
                        id="selected-file-title",
                        className="font-weight-bold",
                    ),
                ]
            ),
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
                            html.H6("Settings"),
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
                        html.Div(id="", style={"display": "none"}),
                        html.P(
                            "モデル",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="モデルの選択",
                        ),
                        html.P(
                            "各変数選択",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="objective-variable",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="目的変数",
                        ),
                        dcc.Dropdown(
                            id="explanatory-variable",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="説明変数",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="モデルの実行",
                            className=" text-white setting_buttom",
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
