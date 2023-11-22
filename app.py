import glob
import os

import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_uploader as du
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from pages import home, page1, page2, page3

uploaded_files_dict = {}
page_layouts = {
    "/": home.layout,
    "/page1": page1.layout,
    "/page2": page2.layout,
    "/page3": page3.layout,
}
external_stylesheets = [dbc.themes.FLATLY, dbc.icons.FONT_AWESOME]
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
)
app.title = "テストページ"
passPair = {"User1": "AAA", "User2": "BBB"}
auth = dash_auth.BasicAuth(app, passPair)
du.configure_upload(app, r"/usr/src/data")


for filepath in glob.glob("data/*/*"):
    filename = os.path.basename(filepath)
    uploaded_files_dict[filename] = filepath

sidebar = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.DropdownMenu(
                            children=[
                                dbc.DropdownMenuItem("home", href="/"),
                                dbc.DropdownMenuItem("Page 1", href="/page1"),
                                dbc.DropdownMenuItem("Page 2", href="/page2"),
                                dbc.DropdownMenuItem("Page 3", href="/page3"),
                            ],
                            label="分析方法の変更",
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


content = html.Div(id="page-content")

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dcc.Location(id="url", refresh=False),
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
                    id="content",
                    width=10,
                ),
            ],
            justify="start",
        )
    ],
    fluid=True,
)


@app.callback([Output("page-content", "children")], [Input("url", "pathname")])
def display_page(pathname):
    return_content = page_layouts.get(pathname, "404 not found")
    return [return_content]


@app.callback(
    Output("sidebar", "style"),
    Output("content", "style"),
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


@app.callback(
    Output("uploaded-files-dropdown", "options"),
    [
        Input("file-reload-button", "n_clicks"),
        Input("delete-confirm-button", "n_clicks"),
    ],
    [State("uploaded-files-dropdown", "value")],
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
        return [{"label": i, "value": i} for i in uploaded_files]

    elif button_id == "delete-confirm-button":
        if n2:
            os.remove(uploaded_files_dict[value])  # ファイルを削除
            del uploaded_files_dict[value]  # 辞書から削除
            uploaded_files = list(uploaded_files_dict.keys())
            return [{"label": i, "value": i} for i in uploaded_files]
        else:
            raise dash.exceptions.PreventUpdate


@app.callback(
    Output("file-select-button", "n_clicks"),
    Input("uploaded-files-dropdown", "value"),
)
def reset_button_on_new_file(value):
    return 0


@app.callback(
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


@app.callback(
    Output("download-csv", "data"),
    Input("download-button", "n_clicks"),
    State("uploaded-files-dropdown", "value"),
    State("input-box", "value"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, value, input_value):
    if n_clicks:
        df = pd.read_csv(uploaded_files_dict[value])
        if input_value:
            filename = f"{input_value}.csv"
        else:
            filename = f"{value}"
        return dcc.send_string(df.to_csv(index=False), filename)


@app.callback(
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


if __name__ == "__main__":
    app.run_server(port=5000, debug=True, host="0.0.0.0", use_reloader=True)
