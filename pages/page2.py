import statistics
from typing import List

import cudf
import dash_bootstrap_components as dbc
import numpy as np
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
                                ),
                            ],
                            className="align-items-center",
                        ),
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
                    [
                        html.Div(
                            [
                                html.P(
                                    id="page2-stats-title",
                                    className="font-weight-bold",
                                    style={
                                        "margin-top": "16px",
                                        "margin-bottom": "4px",
                                    },
                                ),
                                html.P(
                                    html.Table(id="page2-stats-table"),
                                    style={"height": "80vh", "overflow": "scroll"},
                                ),
                            ],
                        ),
                    ],
                    width="6",
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.P(
                                    id="page2-defi-title",
                                    className="font-weight-bold",
                                    style={
                                        "margin-top": "16px",
                                        "margin-bottom": "4px",
                                    },
                                ),
                                html.P(
                                    html.Table(id="page2-defi-table"),
                                    style={"height": "15vh", "overflow": "scroll"},
                                ),
                                html.P(
                                    id="page2-outlier-count-title",
                                    className="font-weight-bold",
                                    style={
                                        "margin-top": "16px",
                                        "margin-bottom": "4px",
                                    },
                                ),
                                html.P(
                                    html.Table(id="page2-outlier-count-table"),
                                    style={"height": "15vh", "overflow": "scroll"},
                                ),
                                html.P(
                                    id="page2-outlier-title",
                                    className="font-weight-bold",
                                    style={
                                        "margin-top": "16px",
                                        "margin-bottom": "4px",
                                    },
                                ),
                                html.P(
                                    html.Table(id="page2-outlier-table"),
                                    style={"height": "40vh", "overflow": "scroll"},
                                ),
                            ],
                        ),
                    ],
                    width="6",
                ),
            ],
            style={"height": "10%"},
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
                            value="cont0",  # ここ注意
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

    df = cudf.read_csv(data)
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

    df = cudf.read_csv(data)

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
    df = cudf.read_csv(data)
    selected_file = data.split("/")
    selected_file_name = f"選択中ファイル：{selected_file[-1]}"

    if df[cont_pick].dtype.kind in "biufc":
        # 数値型の場合
        stats_df = (
            df.groupby(cat_pick)[cont_pick]
            .agg(["count", "mean", "std", "median"])
            .reset_index()
        )
        stats_df_info = stats_df.loc[
            :,
            [
                cat_pick,
                "count",
                "mean",
                "std",
                "median",
            ],
        ]
        stats_df_info.columns = [
            cat_pick,
            "件数",
            "平均",
            "標準偏差",
            "中央値",
        ]
    else:
        # 数値型でない場合
        # 空白を削除してから .agg(["count"]) を実行
        count_df = (
            df.groupby(cat_pick)[cont_pick]
            .apply(lambda x: x.dropna().count())
            .reset_index()
        )

        mode_df = (
            df.groupby(cat_pick)[cont_pick]
            .apply(lambda x: x.mode(dropna=False))
            .reset_index()
        )
        mode_df = mode_df.drop(columns=["index"])
        count_df.columns = [
            f"{col}_count" if col != cat_pick else col for col in count_df.columns
        ]
        mode_df.columns = [
            f"{col}_mode" if col != cat_pick else col for col in mode_df.columns
        ]
        stats_df_info = cudf.concat([count_df, mode_df], axis=1)

        stats_df_info.columns = [
            cat_pick,
            "データ件数",
            "最頻値",
        ]

    table_columns = stats_df_info.columns
    table = dbc.Table.from_dataframe(
        stats_df_info,
        columns=table_columns,
        striped=True,
        bordered=True,
        hover=True,
        style={
            "writingMode": "horizontal-rl",
            "textOrientation": "mixed",
            "whiteSpace": "nowrap",
        },
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

    df = cudf.read_csv(data)

    # 欠損値の数
    defi_se = df.isnull().sum()
    defi_df = cudf.DataFrame(defi_se)
    defi_df_T = defi_df.T
    defi_df_columns = defi_df_T.columns
    table_missing = dbc.Table.from_dataframe(
        defi_df_T,
        columns=defi_df_columns,
        striped=True,
        bordered=True,
        hover=True,
        style={
            "writingMode": "horizontal-rl",
            "textOrientation": "mixed",
            "whiteSpace": "nowrap",
        },
    )
    stats_title = "項目ごとの欠損値の数"

    return table_missing, stats_title


# 外れ値を表示するコールバック
@callback(
    Output("page2-outlier-count-table", "children"),
    Output("page2-outlier-table", "children"),
    Output("page2-outlier-count-title", "children"),
    Output("page2-outlier-title", "children"),
    Input("page2-setting-change-button", "n_clicks"),
    Input("shared-selected-df", "data"),
)
def update_page2_outlier_table(n_clicks, data):
    if data is None:
        return "", ""

    df = cudf.read_csv(data)

    # 外れ値の数 (IQR法を使用)
    numeric_columns = df.select_dtypes(include=np.number).columns
    q1 = df[numeric_columns].quantile(0.25)
    q3 = df[numeric_columns].quantile(0.75)
    iqr = q3 - q1

    # 外れ値の具体的な値
    outliers = (df[numeric_columns] < (q1 - 1.5 * iqr)) | (
        df[numeric_columns] > (q3 + 1.5 * iqr)
    )
    # 外れ値カウント
    outliers_count_se = df[outliers].count()
    outliers_count_df = cudf.DataFrame(outliers_count_se).T
    outliers_count_df_columns = outliers_count_df.columns
    table_outliers_count = dbc.Table.from_dataframe(
        outliers_count_df,
        columns=outliers_count_df_columns,
        striped=True,
        bordered=True,
        hover=True,
        style={
            "writingMode": "horizontal-rl",
            "textOrientation": "mixed",
            "whiteSpace": "nowrap",
        },
    )
    # 具体的な外れ値
    outliers_df = df[outliers].dropna(how="all")
    table_outliers = dbc.Table.from_dataframe(
        outliers_df,  # Display only the first few rows of outliers for brevity
        striped=True,
        bordered=True,
        hover=True,
        style={
            "writingMode": "horizontal-rl",
            "textOrientation": "mixed",
            "whiteSpace": "nowrap",
        },
    )
    outliers_count_title = "外れ値の数"
    outliers_table_title = "外れ値"

    return (
        table_outliers_count,
        table_outliers,
        outliers_count_title,
        outliers_table_title,
    )


# 入力データを表示するコールバック
@callback(
    Output("page2-matrix-selected-file", "children"),
    Output("table2", "columns"),
    Output("table2", "data"),
    Input("shared-selected-df", "data"),
)
def update_table(data):
    df = cudf.read_csv(data)
    selectedfile = data.split("/")
    columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
    data = df.to_dict("records")
    return selectedfile[-1], columns, data
