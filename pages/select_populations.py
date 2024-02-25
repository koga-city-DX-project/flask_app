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
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            html.P(
                "ダッシュボード選択",
                style={
                    "marginTop": "8px",
                    "marginBottom": "0",
                    "fontSize": "1.3em",
                },
                className="font-weight-bold",
            ),
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "高齢化率(行政区・小学校区別)",
                        href="/aging_rate",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link="true",
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "fontSize": "1.3em"},
                    ),
                    width=6,
                    className="d-flex align-items-stretch",
                ),
                dbc.Col(
                    dbc.Button(
                        "人口分布の推移(古賀市・福岡県・国)",
                        href="/population_distribution",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link="true",
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "fontSize": "1.3em"},
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
                        "死因(古賀市・福岡県・国)",
                        href="/cause_death",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link="true",
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "fontSize": "1.3em"},
                    ),
                    width=6,
                    className="d-flex align-items-stretch",
                ),
                dbc.Col(
                    dbc.Button(
                        "○○ページ",
                        href="#",
                        className="menu_btn d-flex align-items-center justify-content-center",
                        external_link="true",
                        color="dark",
                        outline=True,
                        style={"minHeight": "100px", "fontSize": "1.3em"},
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
                            html.Img(
                                src="assets/images/KURA.png",
                                style={"height": "40px", "width": "50%"},
                                alt="KURA",
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
                            color="secondary",
                        ),
                        dbc.Button(
                            href="/select_populations",
                            children="人口",
                            className=" text-white setting_button",
                            color="secondary",
                            disabled=True,
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
                    className="bg-primary bg-opacity-25",
                    width=2,
                ),
                dbc.Col(
                    contents,
                    className="bg-light",
                    width=10,
                ),
            ]
        )
    ]
)
