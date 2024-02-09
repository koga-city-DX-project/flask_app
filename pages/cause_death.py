import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("死因(古賀市・福岡県・国)")],
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
                            id="cause-death-comparison-type-dropdown",
                            options=[
                                {"label": "人数", "value": "people"},
                                {"label": "割合", "value": "rate"},
                            ],
                            value="people",
                            className="setting_dropdown",
                            placeholder="人数で比較",
                        ),
                        html.P("年代", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-age-dropdown",
                            options=[
                                {"label": "0歳～4歳", "value": "0-4"},
                                {"label": "5歳～9歳", "value": "5-9"},
                                {"label": "10歳～14歳", "value": "10-14"},
                                {"label": "15歳～19歳", "value": "15-19"},
                                {"label": "20歳～24歳", "value": "20-24"},
                                {"label": "25歳～29歳", "value": "25-29"},
                                {"label": "30歳～34歳", "value": "30-34"},
                                {"label": "35歳～39歳", "value": "35-39"},
                                {"label": "40歳～44歳", "value": "40-44"},
                                {"label": "45歳～49歳", "value": "45-49"},
                                {"label": "50歳～54歳", "value": "50-54"},
                                {"label": "55歳～59歳", "value": "55-59"},
                                {"label": "60歳～64歳", "value": "60-64"},
                                {"label": "65歳～69歳", "value": "65-69"},
                                {"label": "70歳～74歳", "value": "70-74"},
                                {"label": "75歳～79歳", "value": "75-79"},
                                {"label": "80歳～84歳", "value": "80-84"},
                                {"label": "85歳～89歳", "value": "85-89"},
                                {"label": "90歳～94歳", "value": "90-94"},
                                {"label": "95歳～99歳", "value": "95-99"},
                                {"label": "100歳～", "value": "100-"},
                                {"label": "総数", "value": "all"},
                            ],
                            value="all",
                            className="setting_dropdown",
                            placeholder="全年代の合計人数を表示",
                        ),
                        html.P("性別", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-sex-type-dropdown",
                            options=[
                                {"label": "男性", "value": "男性"},
                                {"label": "女性", "value": "女性"},
                                {"label": "男女計", "value": "男女計"},
                            ],
                            value="男女計",
                            className="setting_dropdown",
                            placeholder="男女合計人数を表示",
                        ),
                        html.P("分類", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-category-dropdown",
                            options=[],
                            value="腸管感染症",
                            placeholder="すべての地域を表示",
                            className="setting_dropdown",
                        ),
                        html.P("比較地域", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-area-dropdown",
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
                        dbc.Button(
                            id="cause-death-download-button",
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
