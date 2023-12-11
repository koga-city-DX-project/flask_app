import glob
import os

import cudf
import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import Input, Output, State, callback, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer

external_stylesheets = [dbc.themes.FLATLY, dbc.icons.FONT_AWESOME]
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
)
du.configure_upload(app, r"/usr/src/data")

uploaded_files_dict = {}
for filepath in glob.glob("data/*/*"):
    filename = os.path.basename(filepath)
    uploaded_files_dict[filename] = filepath

sidebarToggleBtn = dbc.Button(
    children=[html.I(className="fas fa-bars", style={"color": "#c2c7d0"})],
    color="dark",
    className="opacity-50",
    id="sidebar-button",
)

processing_contents = html.Div(
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
                                id="page3-table",
                                columns=[],
                                data=[],
                                editable=True,
                                virtualization=True,
                                page_current=0,
                                page_size=100,
                                style_table={"overflowX": "auto"},
                                page_action="custom",
                                style_header={
                                    "backgroundColor": "rgb(44,62,80)",
                                    "color": "white",
                                },
                            ),
                        ],
                    ),
                ]
            ),
            style={"margin": "8px", "height": "100vh"},
        ),
    ],
)

sidebar = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.DropdownMenu(
                            children=[
                                dbc.DropdownMenuItem("home", href="/home"),
                                dbc.DropdownMenuItem("sample", href="/page1"),
                                dbc.DropdownMenuItem("データ分析", href="/page2"),
                                dbc.DropdownMenuItem("データ加工・編集", href="/processing"),
                                dbc.DropdownMenuItem("モデルの実行", href="/page4"),
                            ],
                            label="データ分析",
                            className="justify-content-start changePageDropDown",
                            color="secondary",
                        ),
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            [
                du.Upload(
                    text="ここにファイルをドラッグ＆ドロップするか、ファイルを選択してください",
                    id="input",
                    max_file_size=1800,
                    chunk_size=100,
                    filetypes=["csv"],
                    max_files=10,
                    cancel_button=True,
                ),
                html.Br(),
                html.Div("input_info"),
                dbc.Select(
                    id="uploaded-files-dropdown",
                    options=[
                        {"label": i, "value": i} for i in uploaded_files_dict.keys()
                    ],
                    value=next(iter(uploaded_files_dict.keys()), None),
                ),
                dbc.Button(
                    id="file-select-button",
                    n_clicks=0,
                    children="ファイル変更",
                    style={"margin": "3vh 0 3vh 0"},
                    color="secondary",
                ),
                dbc.Button(
                    id="file-reload-button",
                    n_clicks=0,
                    children="ファイル更新",
                    style={"margin": "0 0 3vh 0"},
                    className="text-white",
                    color="secondary",
                ),
                dbc.Button(
                    id="file-delete-button",
                    n_clicks=0,
                    children="ファイル削除",
                    className="text-white",
                    color="secondary",
                ),
                html.Hr(),
                dbc.Input(
                    id="input-box",
                    type="text",
                    placeholder="出力ファイルの名前",
                ),
                dbc.Button(
                    "Download Data",
                    id="download-button",
                    n_clicks=0,
                    style={"margin": "3vh 0 3vh 0"},
                    className="text-white",
                    color="secondary",
                ),
                dcc.Download(id="download-csv"),
                html.Hr(),
                dbc.Modal(
                    [
                        dbc.ModalHeader(id="modal_header"),
                        dbc.ModalBody("選択したファイルを削除しますか？"),
                        dbc.ModalFooter(
                            [
                                dbc.Button(
                                    "削除",
                                    id="delete-confirm-button",
                                    className="ml-auto",
                                    color="danger",
                                ),
                                dbc.Button(
                                    "キャンセル",
                                    id="cancel-button",
                                    className="ml-auto",
                                    color="secondary",
                                ),
                            ]
                        ),
                    ],
                    id="modal",
                    is_open=False,
                ),
            ],
            className="center-block sidebar",
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
                            id="delete-col-dropdown",
                            multi=True,
                            className="setting_dropdown",
                            placeholder="列名",
                        ),
                        dbc.Button(
                            id="delete-col-button",
                            n_clicks=0,
                            children="列削除",
                            className=" text-white setting_button",
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
                            className=" text-white setting_button",
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
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        html.Hr(),
                        html.P(
                            "ファイルの統合",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dbc.Select(
                            id="additional-files-dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in uploaded_files_dict.keys()
                            ],
                            value=next(iter(uploaded_files_dict.keys()), None),
                        ),
                        dbc.Button(
                            id="add-file-button",
                            n_clicks=0,
                            children="ファイル追加",
                            className="setting_button",
                            color="secondary",
                        ),
                        dbc.Input(
                            id="rename_file",
                            type="text",
                            placeholder="保存ファイルの名前",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="save-button",
                            n_clicks=0,
                            children="保存",
                            className=" text-white setting_button",
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

content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    settings,
                    className="bg-light",
                    width=2,
                ),
                dbc.Col(
                    processing_contents,
                    width=10,
                ),
            ]
        )
    ]
)
layout = dbc.Container(
    [
        dbc.Row(
            [
                dcc.Store(id="shared-selected-df", storage_type="session"),
                dbc.Col(
                    [
                        dbc.Row(sidebar),
                    ],
                    className="bg-light",
                    width=2,
                    id="sidebar",
                ),
                dbc.Col(
                    content,
                    id="system_content",
                    width=10,
                ),
            ],
            justify="start",
        )
    ],
    fluid=True,
)


@callback(
    Output("sidebar", "style"),
    Output("system_content", "style"),
    Input("sidebar-button", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks):
    if n_clicks:
        if n_clicks % 2 == 1:
            return (
                {"display": "none"},
                {
                    "transition": "width 0.3s ease-in-out",
                    "width": "100%",
                },
            )
        else:
            return (
                {"marginLeft": "0px"},
                {
                    "width": "83.33333%",
                },
            )
    raise PreventUpdate


@du.callback(
    output=Output(
        "uploaded-files-dropdown",
        "options",
        allow_duplicate=True,
    ),
    id="input",
)
def callback_on_completion(status: du.UploadStatus):
    for x in status.uploaded_files:
        filename = os.path.basename(str(x))
        uploaded_files_dict[filename] = str(x)
    uploaded_files = list(uploaded_files_dict.keys())
    return [{"label": i, "value": i} for i in uploaded_files]


@callback(
    Output("uploaded-files-dropdown", "options"),
    Output("additional-files-dropdown", "options"),
    Input("file-reload-button", "n_clicks"),
    Input("delete-confirm-button", "n_clicks"),
    State("uploaded-files-dropdown", "value"),
)
def update_dropdown(n1, n2, value):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "file-reload-button":
        if n1 is None:
            raise PreventUpdate

        for filepath in glob.glob("data/*/*"):
            filename = os.path.basename(filepath)
            uploaded_files_dict[filename] = filepath
        uploaded_files = list(uploaded_files_dict.keys())
        dropdown = [{"label": i, "value": i} for i in uploaded_files]
        return (dropdown, dropdown)

    elif button_id == "delete-confirm-button":
        if n2:
            os.remove(uploaded_files_dict[value])  # ファイルを削除
            del uploaded_files_dict[value]  # 辞書から削除
            uploaded_files = list(uploaded_files_dict.keys())
            dropdown = [{"label": i, "value": i} for i in uploaded_files]
            return (dropdown, dropdown)
        else:
            raise dash.exceptions.PreventUpdate


@callback(
    Output("file-select-button", "n_clicks"),
    Input("uploaded-files-dropdown", "value"),
)
def reset_button_on_new_file(value):
    return 0


@callback(
    Output("file-select-button", "children"),
    Output("shared-selected-df", "data"),
    Input("file-select-button", "n_clicks"),
    State("uploaded-files-dropdown", "value"),
)
def load_new_file(n_clicks, value):
    if n_clicks > 0:
        data = uploaded_files_dict[value]
        return "ファイル変更", data
    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("modal", "is_open"),
    Output("modal_header", "children"),
    [
        Input("file-delete-button", "n_clicks"),
        Input("cancel-button", "n_clicks"),
        Input("delete-confirm-button", "n_clicks"),
    ],
    [
        State("modal", "is_open"),
        State("uploaded-files-dropdown", "value"),
    ],
)
def toggle_modal(n1, n2, n3, is_open, value):
    header_text = f"選択中のファイル：{value}"
    if n1 or n2 or n3:
        return not is_open, header_text
    return is_open, header_text


@callback(
    Output("selected-file-title", "children"),
    Output("page3-table", "data"),
    Output("page3-table", "columns"),
    Output("delete-col-dropdown", "options"),
    Output("missing-value-col-dropdown", "options"),
    Output("scaling-col-dropdown", "options"),
    Input("add-file-button", "n_clicks"),
    Input("delete-col-button", "n_clicks"),
    Input("delete-missing-value-button", "n_clicks"),
    Input("scale-button", "n_clicks"),
    Input("shared-selected-df", "data"),
    Input("page3-table", "page_current"),
    Input("page3-table", "page_size"),
    State("delete-col-dropdown", "value"),
    State("missing-value-col-dropdown", "value"),
    State("missing-value-dropdown", "value"),
    State("scaling-col-dropdown", "value"),
    State("scaling-dropdown", "value"),
    State("additional-files-dropdown", "value"),
)
def update_table(
    add_btn,
    n,
    m,
    s,
    data,
    page_current,
    page_size,
    cols,
    missing_value_cols,
    missing_value_method,
    scaling_cols,
    scaling_method,
    add_file,
):
    global aaa
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = "No clicks yet"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # 選択ファイルの読み込み
    if trigger_id == "shared-selected-df":
        df = cudf.read_csv(data)
        selectedfile = data.split("/")
        print(df.info())
        columns = [
            {"name": i, "id": j, "renamable": True} for i, j in zip(df, df.columns)
        ]
        col_options = [{"label": i, "value": i} for i in df.columns]
        aaa = df
        display_data = df.iloc[
            page_current * page_size : (page_current + 1) * page_size  # NOQA
        ].to_dict("records")
        return (
            selectedfile[-1],
            display_data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    elif trigger_id == "add-file-button" and add_btn > 0:
        additional_file = uploaded_files_dict[add_file]
        selectedfile = data.split("/")
        if additional_file is not None:
            current_df = cudf.DataFrame(aaa)
            additional_df = cudf.read_csv(additional_file)
            df = cudf.concat([current_df, additional_df], ignore_index=True)
            print("合成！")
        data = df.iloc[
            page_current * page_size : (page_current + 1) * page_size  # NOQA
        ].to_dict("records")
        columns = [
            {"name": i, "id": j, "editable": True, "renamable": True}
            for i, j in zip(df, df.columns)
        ]
        col_options = [{"label": i, "value": i} for i in df.columns]
        aaa = df
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
        df = cudf.DataFrame(aaa).drop(columns=cols)
        selectedfile = data.split("/")
        columns = [
            {"name": i, "id": j, "editable": True, "renamable": True}
            for i, j in zip(df, df.columns)
        ]
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = df.iloc[
            page_current * page_size : (page_current + 1) * page_size  # NOQA
        ].to_dict("records")
        aaa = df
        return (
            selectedfile[-1],
            data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    # 欠損値処理
    elif trigger_id == "delete-missing-value-button" and m > 0:
        df = cudf.DataFrame(aaa)
        if not missing_value_cols:
            missing_value_cols = df.columns
        if missing_value_method == "listwise":
            df = df.dropna(subset=missing_value_cols)
        elif missing_value_method == "mean":
            df[missing_value_cols] = df[missing_value_cols].astype(float)
            df[missing_value_cols] = df[missing_value_cols].fillna(
                df[missing_value_cols].mean()
            )

        elif missing_value_method == "mode":
            df[missing_value_cols] = df[missing_value_cols].fillna(
                df[missing_value_cols].mode().iloc[0]
            )
        elif missing_value_method == "imputer":
            imputer = IterativeImputer(max_iter=10, random_state=0)
            df[missing_value_cols] = cudf.DataFrame(
                imputer.fit_transform(df[missing_value_cols]),
                columns=df[missing_value_cols].columns,
            )
        selectedfile = data.split("/")
        columns = [
            {"name": i, "id": j, "editable": True, "renamable": True}
            for i, j in zip(df, df.columns)
        ]
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = df.iloc[
            page_current * page_size : (page_current + 1) * page_size  # NOQA
        ].to_dict("records")
        aaa = df
        return (
            selectedfile[-1],
            data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    # スケーリング処理
    elif trigger_id == "scale-button" and s > 0:
        df = cudf.DataFrame(aaa)
        if not scaling_cols:
            scaling_cols = df.columns
        if scaling_method == "normalize":
            df[scaling_cols] = df[scaling_cols].astype(float)
            df[scaling_cols] = (df[scaling_cols] - df[scaling_cols].min()) / (
                df[scaling_cols].max() - df[scaling_cols].min()
            )
        elif scaling_method == "standardize":
            df[scaling_cols] = df[scaling_cols].astype(float)
            df[scaling_cols] = (df[scaling_cols] - df[scaling_cols].mean()) / df[
                scaling_cols
            ].std()
        selectedfile = data.split("/")
        columns = [
            {"name": i, "id": j, "editable": True, "deletable": True, "renamable": True}
            for i, j in zip(df, df.columns)
        ]
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = df.iloc[
            page_current * page_size : (page_current + 1) * page_size  # NOQA
        ].to_dict("records")
        aaa = df.to_dict("records")
        return (
            selectedfile[-1],
            data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    elif trigger_id == "page3-table":
        df = cudf.DataFrame(aaa)
        display_data = df.iloc[
            page_current * page_size : (page_current + 1) * page_size  # NOQA
        ].to_dict("records")
        return (
            dash.no_update,
            display_data,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
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
        State("rename_file", "value"),
        State("uploaded-files-dropdown", "value"),
    ],
)
def save_table(n_clicks, file_rename_value, file_current_name):
    if n_clicks > 0:
        df = cudf.DataFrame(aaa, dtype=object)
        if file_rename_value:
            filename = f"{file_rename_value}.csv"
        else:
            filename = f"{file_current_name}.csv"
        filepath = f"/usr/src/data/save/{filename}"
        df.to_csv(filepath, index=False)


@callback(
    Output("download-csv", "data"),
    Input("download-button", "n_clicks"),
    State("uploaded-files-dropdown", "value"),
    State("input-box", "value"),
)
def download_csv(n_clicks, value, input_value):
    if n_clicks:
        df = cudf.read_csv(uploaded_files_dict[value])
        if input_value:
            filename = f"{input_value}.csv"
        else:
            filename = f"{value}"
        return dcc.send_string(df.to_csv(index=False), filename)
