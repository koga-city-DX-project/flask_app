from typing import List

import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

vars_cat: List[str] = []
vars_cont: List[str] = []

sidebarToggleBtn = dbc.Button(
    children=[html.I(className="fas fa-bars", style={"color": "#c2c7d0"})],
    color="dark",
    className="opacity-50",
    id="page2-sidebar-button",  # 変更
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
                            html.P(
                                id="page2-stats-title", className="font-weight-bold"
                            ),  # 変更
                            html.Table(id="page2-stats-table"),  # 変更
                        ]
                    ),
                    width=12,
                ),
            ],
            style={
                "margin": "2vh 1vw 1vh 1vw",
            },
        ),
    ],
)

settings = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    sidebarToggleBtn, className="col-2", id="page2-setting_Col"
                ),  # 変更
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
                            id="page2-my-cat-picker",  # 変更
                            multi=False,
                            value="cat0",
                            options=[{"label": x, "value": x} for x in vars_cat],
                            style={"width": "98%"},
                        ),
                        html.P(
                            "連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="page2-my-cont-picker",  # 変更
                            multi=False,
                            value="cont0",
                            options=[{"label": x, "value": x} for x in vars_cont],
                            style={"width": "98%"},
                        ),
                        html.Button(
                            id="page2-setting-change-button",  # 変更
                            n_clicks=0,
                            children="設定変更",
                            style={"margin": "16px auto 0 auto", "width": "95%"},
                            className="bg-dark text-white ",
                        ),
                        html.Hr(),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "50vh", "margin-left": "1px"},
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


# カテゴリー変数の選択肢を更新するコールバック
@callback(
    Output("page2-my-cat-picker", "options"),  # 変更
    [Input("shared-selected-df", "data")],
)
def update_page2_cat_picker_options(data):  # 変更
    if data is None:
        return []

    df = pd.read_csv(data)
    vars_cat = [var for var in df.columns if var.startswith("cat")]

    options_cat = [{"label": x, "value": x} for x in vars_cat]

    return options_cat


# 連続変数の選択肢を更新するコールバック
@callback(
    Output("page2-my-cont-picker", "options"),
    [Input("shared-selected-df", "data")],
)
def update_page2_cont_picker_options(data):
    if data is None:
        return []

    df = pd.read_csv(data)
    vars_cont = [var for var in df.columns if var.startswith("cont")]

    options_cont = [{"label": x, "value": x} for x in vars_cont]

    return options_cont


# データの基本統計量を表示するコールバック
@callback(
    Output("page2-stats-table", "children"),
    Output("page2-stats-title", "children"),
    Input("page2-setting-change-button", "n_clicks"),
    Input("shared-selected-df", "data"),
    State("page2-my-cat-picker", "value"),
    State("page2-my-cont-picker", "value"),
)
def update_page2_stats_table(n_clicks, data, cat_pick, cont_pick):
    if data is None:
        return "", ""

    df = pd.read_csv(data)

    if cat_pick and cont_pick and cont_pick in df.columns:
        stats_df = df.groupby(cat_pick)[cont_pick].describe().reset_index()
        print(stats_df.columns)  # debug

        # 'Statistics' という列が存在しない場合は新しく追加する
        if "Statistics" not in stats_df.columns:
            stats_df["Statistics"] = ""

        stats_df.columns = [
            "Statistics" if col == cont_pick else col for col in stats_df.columns
        ]

        # 'Statistics' 列が浮動小数点数として扱われるように変更
        stats_df["Statistics"] = stats_df["Statistics"].apply(
            lambda x: round(float(x), 2) if x != "" else x
        )
        print(stats_df.columns)  # debug

        stats_df = stats_df.T.reset_index()
        stats_df.columns = stats_df.iloc[0]
        stats_df = stats_df.drop(0).reset_index(drop=True)
        stats_df = stats_df.rename(columns={stats_df.columns[0]: ""})
        stats_title = f"{cat_pick}ごとの{cont_pick}の基本統計量"

        return (
            dbc.Table.from_dataframe(stats_df, striped=True, bordered=True, hover=True),
            stats_title,
        )

    return "", ""
