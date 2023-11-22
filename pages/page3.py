import cudf
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dash_table, dcc, html
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer

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
                    dcc.Loading(
                        id="loading",
                        type="circle",
                        className="dash-loading-callback",
                        children=[
                            dash_table.DataTable(
                                id="table",
                                columns=[],
                                data=[],
                                virtualization=True,
                                style_table={"overflowX": "auto"},
                            ),
                        ],
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
                        html.Div(id="store-data", style={"display": "none"}),
                        html.P(
                            "列の削除",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="col-dropdown",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="列名",
                        ),
                        dbc.Button(
                            id="delete-col-button",
                            n_clicks=0,
                            children="列削除",
                            className=" text-white setting_buttom",
                            color="secondary",
                        ),
                        html.P(
                            "欠損値",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="missing-value-col-dropdown",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="列名",
                        ),
                        dcc.Dropdown(
                            id="missing-value-dropdown",
                            options=[
                                {"label": "リストワイズ削除", "value": "listwise"},
                                {"label": "平均値代入法", "value": "mean"},
                                {"label": "最頻値代入法", "value": "mode"},
                                {"label": "多重代入法", "value": "imputer"},
                            ],
                            className="setting_dropdown",
                            placeholder="手法の選択",
                        ),
                        dbc.Button(
                            id="delete-missing-value-button",
                            n_clicks=0,
                            children="実行",
                            className=" text-white setting_buttom",
                            color="secondary",
                        ),
                        html.P(
                            "スケーリング",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="scaling-col-dropdown",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="列名",
                        ),
                        dcc.Dropdown(
                            id="scaling-dropdown",
                            options=[
                                {"label": "正規化", "value": "normalize"},
                                {"label": "標準化", "value": "standardize"},
                            ],
                            className="setting_dropdown",
                            placeholder="手法の選択",
                        ),
                        dbc.Button(
                            id="scale-button",
                            n_clicks=0,
                            children="実行",
                            className=" text-white setting_buttom",
                            color="secondary",
                        ),
                        html.Hr(),
                        dbc.Input(
                            id="rename_file",
                            type="text",
                            placeholder="保存ファイルの名前",
                            className="setting_buttom",
                        ),
                        dbc.Button(
                            id="save-button",
                            n_clicks=0,
                            children="保存",
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


@callback(
    Output("selected-file-title", "children"),
    Output("table", "data"),
    Output("table", "columns"),
    Output("col-dropdown", "options"),
    Output("missing-value-col-dropdown", "options"),
    Output("scaling-col-dropdown", "options"),
    Input("delete-col-button", "n_clicks"),
    Input("delete-missing-value-button", "n_clicks"),
    Input("scale-button", "n_clicks"),
    Input("shared-selected-df", "data"),
    State("col-dropdown", "value"),
    State("missing-value-col-dropdown", "value"),
    State("missing-value-dropdown", "value"),
    State("scaling-col-dropdown", "value"),
    State("scaling-dropdown", "value"),
    State("table", "data"),
)
def update_table(
    n,
    m,
    s,
    data,
    cols,
    missing_value_cols,
    missing_value_method,
    scaling_cols,
    scaling_method,
    table_data,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = "No clicks yet"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # 選択ファイルの読み込み
    if trigger_id == "shared-selected-df":
        df = cudf.read_csv(data, dtype=object)
        selectedfile = data.split("/")
        columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = df.to_dict("records")
        return (
            selectedfile[-1],
            data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    # 列削除
    elif trigger_id == "delete-col-button" and n > 0:
        df = cudf.DataFrame(table_data, dtype=object).drop(columns=cols)
        selectedfile = data.split("/")
        columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
        col_options = [{"label": i, "value": i} for i in df.columns]
        return (
            selectedfile[-1],
            df.to_dict("records"),
            columns,
            col_options,
            col_options,
            col_options,
        )
    # 欠損値処理
    elif trigger_id == "delete-missing-value-button" and m > 0:
        df = cudf.DataFrame(table_data, dtype=object)
        print(type(missing_value_cols))
        if not missing_value_cols:
            missing_value_cols = df.columns
            print(missing_value_cols)
        if missing_value_method == "listwise":
            df = df.dropna(subset=missing_value_cols)
        elif missing_value_method == "mean":
            df[missing_value_cols] = df[missing_value_cols].fillna(
                df[missing_value_cols].mean()
            )
        elif missing_value_method == "mode":
            df[missing_value_cols] = df[missing_value_cols].fillna(
                df[missing_value_cols].mode().iloc[0]
            )
        elif missing_value_method == "imputer":
            imputer = IterativeImputer()
            df[missing_value_cols] = cudf.DataFrame(
                imputer.fit_transform(df[missing_value_cols]),
                columns=df[missing_value_cols].columns,
            )
        selectedfile = data.split("/")
        columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
        col_options = [{"label": i, "value": i} for i in df.columns]
        return (
            selectedfile[-1],
            df.to_dict("records"),
            columns,
            col_options,
            col_options,
            col_options,
        )
    # スケーリング処理
    elif trigger_id == "scale-button" and s > 0:
        df = cudf.DataFrame(table_data, dtype=object)
        if not scaling_cols:
            scaling_cols = df.columns
        if scaling_method == "normalize":
            df[scaling_cols] = (df[scaling_cols] - df[scaling_cols].min()) / (
                df[scaling_cols].max() - df[scaling_cols].min()
            )
        elif scaling_method == "standardize":
            df[scaling_cols] = (df[scaling_cols] - df[scaling_cols].mean()) / df[
                scaling_cols
            ].std()
        selectedfile = data.split("/")
        columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
        col_options = [{"label": i, "value": i} for i in df.columns]
        return (
            selectedfile[-1],
            df.to_dict("records"),
            columns,
            col_options,
            col_options,
            col_options,
        )
    else:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )


@callback(
    Output("store-data", "children"),
    [Input("save-button", "n_clicks")],
    [
        State("table", "data"),
        State("rename_file", "value"),
        State("uploaded-files-dropdown", "value"),
    ],
)
def save_table(n_clicks, table_data, file_rename_value, file_current_name):
    if n_clicks > 0:
        df = cudf.DataFrame(table_data, dtype=object)
        if file_rename_value:
            filename = f"{file_rename_value}.csv"
        else:
            filename = f"{file_current_name}.csv"
        filepath = f"/usr/src/data/save/{filename}"
        df.to_csv(filepath, index=False)
