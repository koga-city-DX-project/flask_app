import dash_bootstrap_components as dbc
from dash import dcc, html

contents = html.Div(
    [
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
                html.Div("a"),
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
                            "表示期間",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="",
                            options=[
                                {"label": "年ごと", "value": "Y"},
                                {"label": "月ごと", "value": "M"},
                            ],
                            value="Y",
                            className="setting_dropdown",
                            placeholder="表示期間を選択",
                        ),
                        html.P(
                            "自治コード別",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="",
                            options=[
                                {"label": "指定なし", "value": "city0"},
                                {"label": "○○市", "value": ""},
                                {"label": "○○町", "value": ""},
                            ],
                            value="city0",
                            className="setting_dropdown",
                            placeholder="自治コード別にみる",
                        ),
                        html.P(
                            "介護度別",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="",
                            options=[
                                {"label": "指定なし", "value": "k0"},
                                {"label": "要介護5", "value": "k5"},
                                {"label": "要介護4", "value": "k4"},
                                {"label": "要介護3", "value": "k3"},
                                {"label": "要介護2", "value": "k2"},
                                {"label": "要介護1", "value": "k1"},
                                {"label": "要支援2", "value": "s2"},
                                {"label": "要支援1", "value": "s1"},
                            ],
                            value="k0",
                            className="setting_dropdown",
                            placeholder="介護度別にみる",
                        ),
                        dbc.Button(
                            href="#",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "35vh", "marginLeft": "1px"},
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
