from typing import List

import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, dash_table, dcc, html
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
                dbc.Col(  # タイトル
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
            html.Div(
                [
                    html.P(
                        id="page2-matrix-selected-file",
                        className="font-weight-bold",
                    ),
                    dcc.Loading(
                        id="loading",
                        type="circle",
                        className="dash-loading-callback",
                        children=[
                            dash_table.DataTable(
                                id="table2",
                                columns=[],
                                data=[],
                                virtualization=True,
                                style_table={
                                    "overflowX": "auto",
                                    "overflowY": "auto",
                                    "height": "300px",
                                },
                            ),
                        ],
                    ),
                ]
            ),
            style={"margin": "8px", "height": "30%"},
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="page2-stats-title", className="font-weight-bold"),
                    width="6",
                ),
                dbc.Col(
                    html.Div(id="page2-defi-title", className="font-weight-bold"),
                    width="6",
                ),
            ],
            style={"height": "10%"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        html.Table(id="page2-stats-table"),
                    ),
                    style={"height": "50vh", "overflow": "scroll"},
                ),
                dbc.Col(
                    html.Div(
                        html.Table(id="page2-defi-table"),
                    ),
                    style={"height": "50vh", "overflow": "scroll"},
                ),
            ],
        ),
        html.Hr(),
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
                            value="cat0",  # ここ注意 出来ればデータによって自動で変更したい
                            options=[{"label": x, "value": x} for x in vars_cat],
                            style={"width": "98%"},
                        ),
                        html.P(
                            "連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="page2-my-cont-picker",
                            multi=False,
                            value="co0",  # ここ注意
                            options=[{"label": x, "value": x} for x in vars_cont],
                            style={"width": "98%"},
                        ),
                        html.P(
                            "相関行列の連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="page2-corr-picker",
                            multi=True,
                            value=vars_cont + ["target"],
                            options=[
                                {"label": x, "value": x} for x in vars_cont + ["target"]
                            ],
                            style={"width": "98%"},
                        ),
                        html.Button(
                            id="page2-setting-change-button",
                            n_clicks=0,
                            children="設定変更",
                            style={"margin-top": "16px", "width": "95%"},
                            className="bg-dark text-white ",
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
    options_cat = [{"label": col, "value": col} for col in df.columns]

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

    options_cont = [{"label": x, "value": x} for x in df.columns]

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
    df = pd.read_csv(data)
    print(df)
    selected_file = data.split("/")
    selected_file_name = f"選択中ファイル：{selected_file[-1]}"
    stats_df = df.groupby(cat_pick)[cont_pick].describe().reset_index()
    stats_df_info = stats_df.loc[
        :,
        [
            cat_pick,
            "count",
            "mean",
            "std",
            "50%",
        ],
    ]
    stats_df_info.columns = [
        cat_pick,
        "件数",
        "平均",
        "標準偏差",
        "中央値",
    ]
    table_columns = stats_df_info.columns
    table = dbc.Table.from_dataframe(
        stats_df_info,
        columns=table_columns,
        striped=True,
        bordered=True,
        hover=True,
    )

    stats_title = f"{cat_pick}ごとの{cont_pick}の基本統計量"
    return table, stats_title, selected_file_name


# データの欠損値を表示するコールバック
@callback(
    Output("page2-defi-table", "children"),
    Output("page2-defi-title", "children"),
    Input("page2-setting-change-button", "n_clicks"),
    Input("shared-selected-df", "data"),
)
def update_page2_defi_table(n_clicks, data):
    if data is None:
        return "", ""

    df = pd.read_csv(data)
    defi_se = df.isnull().sum()
    defi_df = pd.DataFrame(defi_se)
    defi_df_T = defi_df.T
    defi_df_columns = defi_df_T.columns
    table = dbc.Table.from_dataframe(
        defi_df_T,
        columns=defi_df_columns,
        striped=True,
        bordered=True,
        hover=True,
    )

    stats_title = "項目ごとの欠損値の数"
    return table, stats_title


# 入力データを表示するコールバック
@callback(
    Output("page2-matrix-selected-file", "children"),
    Output("table2", "columns"),
    Output("table2", "data"),
    Input("shared-selected-df", "data"),
)
def update_table(data):
    df = pd.read_csv(data, low_memory=False)
    selectedfile = data.split("/")
    columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
    data = df.to_dict("records")
    return selectedfile[-1], columns, data
