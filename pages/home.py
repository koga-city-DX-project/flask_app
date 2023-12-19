import glob
import os
import time
from typing import Optional

import cudf
import dash
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import Input, Output, State, callback, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer

current_table: Optional[cudf.DataFrame] = None
external_stylesheets = ["bootstrap.min.css", "/assets/css/all.min.css"]
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

column_types = {
    "外国人の住民区分名": "object",
    "続柄": "object",
    "死亡日": "object",
}

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
                                style_table={
                                    "minHeight": "50vh",
                                },
                                page_action="custom",
                                style_header={
                                    "backgroundColor": "rgb(44,62,80)",
                                    "color": "white",
                                },
                            ),
                        ],
                    ),
                    html.Hr(),
                    dbc.Button(
                        id="table-reload-button",
                        n_clicks=0,
                        children="テーブルを再読込",
                        style={"margin": "3vh 0 3vh 0"},
                        color="secondary",
                    ),
                    html.Div("※ロードが続く場合は再読込を押してください"),
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
                html.P(
                    "ファイルを選択",
                    style={
                        "marginTop": "8px",
                        "marginBottom": "4px",
                    },
                    className="font-weight-bold",
                ),
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
                    style={"margin": "0 0 3vh 0"},
                    className="text-white",
                    color="secondary",
                ),
                dbc.Input(
                    id="input-box",
                    type="text",
                    placeholder="出力ファイルの名前",
                ),
                dbc.Button(
                    "Download Data",
                    id="download-button",
                    n_clicks=0,
                    style={"margin": "1vh 0 3vh 0"},
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
                                "marginTop": "8px",
                                "marginBottom": "4px",
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
                            "レコードの追加",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
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
                        html.P(
                            "pk・fkでの統合",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="pk-additional-files-dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in uploaded_files_dict.keys()
                            ],
                            value=next(iter(uploaded_files_dict.keys()), None),
                            placeholder="追加ファイルを選択",
                        ),
                        dcc.Dropdown(
                            id="pkfk-column-dropdown",
                            options=[],
                            placeholder="紐づける列名",
                        ),
                        dcc.Dropdown(
                            id="additional-column-dropdown",
                            options=[],
                            multi=True,
                            placeholder="追加する列名",
                        ),
                        dcc.Dropdown(
                            id="date-column-dropdown",
                            options=[],
                            placeholder="参照する日時列",
                        ),
                        dbc.Button(
                            id="pk-add-file-button",
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
                        html.Div(id="file-save-message"),
                        html.Hr(),
                        html.P(
                            "欠損値",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
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
                                "marginTop": "8px",
                                "marginBottom": "4px",
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
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "130vh", "marginLeft": "1px"},
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
                dcc.Store(id="current-table-store"),
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
            delete_table_columns()
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
    Input("pk-add-file-button", "n_clicks"),
    Input("delete-confirm-button", "n_clicks"),
    Input("table-reload-button", "n_clicks"),
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
    pk_add_file,
    delete_confirm,
    table_reload_btn,
    cols,
    missing_value_cols,
    missing_value_method,
    scaling_cols,
    scaling_method,
    add_file,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = "No clicks yet"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # 選択ファイルの読み込み
    if trigger_id == "shared-selected-df":
        print("読み込み！")
        df = cudf.read_csv(data)

        df = convert_column_types(df, column_types)
        store_current_table(df)
        selectedfile = data.split("/")
        print(f"{selectedfile[-1]}:{df.info()}")
        columns = get_table_columns(df)
        col_options = [{"label": i, "value": i} for i in df.columns]
        display_data = get_display_table(df, page_current, page_size)
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
            df = cudf.DataFrame(get_current_table())
            additional_df = cudf.read_csv(additional_file)
            additional_df = convert_column_types(additional_df, column_types)
            if not set(additional_df.columns).issubset(df.columns):
                error_message = "エラー：カラム名が一致しません"
                return (
                    error_message,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                )
            try:
                additional_df = align_dataframe_columns_and_types(df, additional_df)
                df = cudf.concat([df, additional_df], ignore_index=True)
            except ValueError as e:
                error_message = str(e)
                return (
                    error_message,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                )
            print("合成！")
        data = get_display_table(df, page_current, page_size)
        columns = get_table_columns(df)
        col_options = [{"label": i, "value": i} for i in df.columns]
        store_current_table(df)
        file_and_message = f"{selectedfile[-1]}    ※{add_file}を追加しました"
        return (
            file_and_message,
            data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    # 列削除
    elif trigger_id == "delete-col-button" and n > 0:
        df = cudf.DataFrame(get_current_table()).drop(columns=cols)
        selectedfile = data.split("/")
        columns = get_table_columns(df)
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = get_display_table(df, page_current, page_size)
        store_current_table(df)
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
        df = cudf.DataFrame(get_current_table())
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
        columns = get_table_columns(df)
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = get_display_table(df, page_current, page_size)
        store_current_table(df)
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
        df = cudf.DataFrame(get_current_table())
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
        columns = get_table_columns(df)
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = get_display_table(df, page_current, page_size)
        store_current_table(df)
        return (
            selectedfile[-1],
            data,
            columns,
            col_options,
            col_options,
            col_options,
        )
    elif trigger_id == "page3-table" or trigger_id == "table-reload-button":
        df = cudf.DataFrame(get_current_table())
        display_data = get_display_table(df, page_current, page_size)
        return (
            dash.no_update,
            display_data,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    elif trigger_id == "pk-add-file-button" and pk_add_file > 0:
        time.sleep(60)
        df = cudf.DataFrame(get_current_table())
        display_data = get_display_table(df, page_current, page_size)
        columns = get_table_columns(df)
        return (
            dash.no_update,
            display_data,
            columns,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    elif trigger_id == "delete-confirm-button" and delete_confirm > 0:
        time.sleep(1)
        print(get_current_table())
        df = cudf.DataFrame(get_current_table())
        display_data = get_display_table(df, page_current, page_size)
        columns = get_table_columns(df)
        return (
            "ファイルが削除されました！！",
            display_data,
            columns,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    elif get_current_table() is None:
        return (
            "ファイルが未選択です！！",
            dash.no_update,
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
    Output("file-save-message", "children"),
    Output("file-save-message", "style"),
    [Input("save-button", "n_clicks")],
    [
        State("rename_file", "value"),
        State("uploaded-files-dropdown", "value"),
    ],
)
def save_table(n_clicks, file_rename_value, file_current_name):
    if n_clicks is not None and n_clicks > 0:
        df = cudf.DataFrame(get_current_table(), dtype=object)
        if file_rename_value:
            filename = f"{file_rename_value}.csv"
        else:
            filename = f"{file_current_name}.csv"
        filepath = f"/usr/src/data/save/{filename}"
        df.to_csv(filepath, index=False)
        return f"{filename}として保存しました", {"display": "block"}
    else:
        return "", {"display": "none"}


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
            filename = f"{input_value}"
        else:
            filename = f"{value}"
        return dcc.send_string(df.to_csv(index=False), filename)


@callback(
    [
        Output("pkfk-column-dropdown", "options"),
        Output("pkfk-column-dropdown", "placeholder"),
        Output("pkfk-column-dropdown", "disabled"),
        Output("additional-column-dropdown", "options"),
        Output("additional-column-dropdown", "disabled"),
        Output("pk-add-file-button", "disabled"),
        Output("date-column-dropdown", "options"),
        Output("date-column-dropdown", "disabled"),
        Output("pk-additional-files-dropdown", "options"),
    ],
    [
        Input("shared-selected-df", "data"),
        Input("pk-additional-files-dropdown", "value"),
        Input("pkfk-column-dropdown", "value"),
        Input("additional-column-dropdown", "value"),
        Input("pk-add-file-button", "n_clicks"),
    ],
    State("date-column-dropdown", "value"),
)
def update_dropdowns_on_file_change(
    data,
    selected_additional_file,
    pkfk_column_value,
    additional_column_value,
    add_btn_clicks,
    date_column,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = "No clicks yet"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if get_current_table() is None:
        print("テーブルは空です")
        return (
            [],
            "紐づける列名を選択",
            True,
            [],
            True,
            True,
            [],
            True,
            dash.no_update,
        )
    if selected_additional_file is None:
        print("追加ファイルが選択されていません")
        return (
            [],
            "紐づける列名を選択",
            True,
            [],
            True,
            True,
            [],
            True,
            dash.no_update,
        )
    if trigger_id == "shared-selected-df":
        additional_files_options = [
            {"label": i, "value": i} for i in uploaded_files_dict.keys()
        ]
        return (
            [],
            "紐づける列名を選択",
            True,
            [],
            True,
            True,
            [],
            True,
            additional_files_options,
        )
    main_table = cudf.DataFrame(get_current_table())
    additional_table = cudf.read_csv(uploaded_files_dict[selected_additional_file])

    common_columns = set(main_table.columns).intersection(additional_table.columns)
    unique_columns = set(additional_table.columns) - common_columns
    int_columns = [col for col in main_table.columns if main_table[col].dtype == "int"]

    if trigger_id == "pk-add-file-button" and add_btn_clicks > 0:
        print("合成中")
        main_table = merge_additional_columns(
            main_table,
            additional_table,
            pkfk_column_value,
            date_column,
            additional_column_value,
        )
        print("合成完了")
        store_current_table(main_table)
        return (
            [],
            "紐づける列名を選択",
            True,
            [],
            True,
            True,
            [],
            True,
            dash.no_update,
        )
    if not common_columns:
        return (
            ["共通の列名がない"],
            "共通の列名がない",
            True,
            [],
            True,
            True,
            [],
            True,
            dash.no_update,
        )
    elif len(common_columns) == len(main_table.columns) and len(common_columns) == len(
        additional_table.columns
    ):
        return (
            ["列名がすべて同じです"],
            "列名がすべて同じです",
            True,
            [],
            True,
            True,
            [],
            True,
            dash.no_update,
        )
    else:
        common_col_options = [{"label": col, "value": col} for col in common_columns]
        unique_col_options = [{"label": col, "value": col} for col in unique_columns]
        date_col_options = [{"label": col, "value": col} for col in int_columns]

        pk_add_file_disabled = not pkfk_column_value or not additional_column_value

        return (
            common_col_options,
            "紐づける列名を選択",
            False,
            unique_col_options,
            False,
            pk_add_file_disabled,
            date_col_options,
            False,
            dash.no_update,
        )


def get_current_table():
    """
    現在のデータフレームを取得する。
    """
    return current_table


def store_current_table(df):
    """
    データフレームをグローバル変数に格納する。
    """
    global current_table
    print("テーブルが更新されました")
    current_table = df


def get_table_columns(df):
    """
    データフレーム内のカラムを取得する。
    """
    if df is None or df.empty:
        return []

    return [
        {"name": col, "id": col, "editable": True, "renamable": True}
        for col in df.columns
    ]


def delete_table_columns():
    """
    データフレームを初期化する
    """
    global current_table
    current_table = None


def align_dataframe_columns_and_types(df, additional_df):
    """
    二つのデータフレームのカラム名とデータ型を整合させる。
    """
    # カラム名の確認
    if set(df.columns) != set(additional_df.columns):
        raise ValueError("エラー：カラム名が一致しません")

    # データ型の整合
    for col in df.columns:
        if df[col].dtype != additional_df[col].dtype:
            print(df[col], additional_df[col])
            additional_df[col] = additional_df[col].astype(df[col].dtype)
            print(f"カラム '{col}' の型変換に成功しました。")

    return additional_df


def get_display_table(df, page_current, page_size):
    """
    ページングされたテーブルを取得する。
    """
    return df.iloc[
        page_current * page_size : (page_current + 1) * page_size  # NOQA
    ].to_dict("records")


def merge_additional_columns(
    main_table,
    additional_table,
    pkfk_column_value,
    date_column,
    additional_column_values,
):
    for i in range(len(main_table)):
        print(f"処理中：{i}/{len(main_table)}")
        matching_records = additional_table[
            additional_table[pkfk_column_value] == main_table.at[i, pkfk_column_value]
        ]
        filtered_records = matching_records[
            matching_records["最新異動日"] <= main_table.at[i, date_column]
        ]

        if not filtered_records.empty:
            latest_record = filtered_records.nlargest(1, "最新異動日").reset_index(drop=True)
            for col in additional_column_values:
                main_table.at[i, col] = latest_record.at[0, col]
        else:
            for col in additional_column_values:
                main_table.at[i, col] = None

    return main_table


def convert_column_types(df, column_types):
    """
    指定されたカラムを指定された型に変換します。
    """
    for column, dtype in column_types.items():
        if column in df.columns:
            try:
                df[column] = df[column].astype(dtype)
                print(f"カラム '{column}' の型変換に成功しました。")
            except Exception as e:
                print(f"型変換エラー: {column} を {dtype} に変換できませんでした。エラー: {e}")
    return df
