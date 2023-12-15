import dash_bootstrap_components as dbc
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
            className="bg-primary text-white font-italic topMenu ",
        ),
        dbc.Row(
            [
                html.P(
                    "ダッシュボード選択",
                    style={
                        "marginTop": "8px",
                        "marginBottom": "0",
                        "fontSize": "1.3em",
                    },
                    className="font-weight-bold",
                ),
            ],
        ),
        html.Hr(),
        dbc.Row(
            [
                html.Div("ダッシュボード一覧～"),
            ]
        ),
        dbc.Row(
            [
                html.Div("ここはテストページです"),
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
                                "marginTop": "8px",
                                "marginBottom": "0",
                                "fontSize": "1.3em",
                            },
                            className="font-weight-bold",
                        ),
                        html.Hr(),
                        dbc.Button(
                            href="/",
                            children="介護",
                            className=" text-white setting_button",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Button(
                            href="/tax",
                            children="税務",
                            className=" text-white setting_button",
                            external_link="true",
                            color="secondary",
                            disabled=True,
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
            style={"height": "25vh", "marginLeft": "1px"},
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
