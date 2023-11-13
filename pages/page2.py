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
                                    "基本統計量",
                                )
                            ],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu ",
        ),
        html.Div(id="page2-selected-file", className="font-weight-bold"),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="page2-stats-title", className="font-weight-bold"),
                    width=12,
                ),
            ],
            style={
                "height": "10%",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        html.Table(id="page2-stats-table"),
                    ),
                    width=12,
                ),
            ],
            style={"overflow": "scroll"},
        ),
        html.Hr(),
        html.Div(
            "↓ここから下に別の結果↓敢えて画面の大きさの50%の大きさでdivタグを取っている",
            style={"height": "50vh"},
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
                            id="page2-my-cat-picker",
                            multi=False,
                            value="cat0",
                            options=[{"label": x, "value": x} for x in vars_cat],
                            className="setting_dropdown",
                        ),
                        html.P(
                            "連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="page2-my-cont-picker",
                            multi=False,
                            value="cont0",
                            options=[{"label": x, "value": x} for x in vars_cont],
                            className="setting_dropdown",
                        ),
                        dbc.Button(
                            id="page2-setting-change-button",
                            n_clicks=0,
                            children="設定変更",
                            style={"margin-top": "16px", "width": "95%"},
                            className="text-white ",
                            color="secondary",
                        ),
                        html.Hr(),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "30vh", "margin-left": "1px"},
        ),
    ],
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
    Output("page2-my-cat-picker", "options"),
    [Input("shared-selected-df", "data")],
)
def update_page2_cat_picker_options(data):
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
    Output("page2-selected-file", "children"),
    Input("page2-setting-change-button", "n_clicks"),
    Input("shared-selected-df", "data"),
    State("page2-my-cat-picker", "value"),
    State("page2-my-cont-picker", "value"),
)
def update_page2_stats_table(n_clicks, data, cat_pick, cont_pick):
    if data is None:
        return "", ""

    df = pd.read_csv(data)
    selected_file = data.split("/")
    selected_file_name = f"選択中ファイル：{selected_file[-1]}"
    if cat_pick and cont_pick and cont_pick in df.columns:
        stats_df = df.groupby(cat_pick)[cont_pick].describe().reset_index()
        stats_df.columns = [
            "Statistics" if col == cont_pick else col for col in stats_df.columns
        ]

        # 'Statistics' 列をデータフレームから取り除く
        stats_df = stats_df.drop("Statistics", axis=1, errors="ignore")

        # データフレームを転置
        stats_df = stats_df.T.reset_index()

        # 列名を変更
        stats_df.columns = stats_df.iloc[0]

        # 不要な行を削除
        stats_df = stats_df.drop(0).reset_index(drop=True)

        # もし "Statistics" 列が存在すれば、それを除外して列名のリストを作成
        table_columns = [col for col in stats_df.columns if col != "Statistics"]

        # dbc.Table.from_dataframe に正しい列名のリストを指定
        table = dbc.Table.from_dataframe(
            stats_df,
            columns=table_columns,
            striped=True,
            bordered=True,
            hover=True,
            style={"height": "70vh"},
        )

        stats_title = f"{cat_pick}ごとの{cont_pick}の基本統計量"

        return table, stats_title, selected_file_name

    return "", "", ""
