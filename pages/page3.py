import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dash_table, dcc, html

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
                        html.P(
                            "列の削除",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="col-dropdown", multi=True, className="setting_dropdown"
                        ),
                        html.Button(
                            id="delete-button",
                            n_clicks=0,
                            children="削除",
                            className="bg-dark text-white setting_buttom",
                        ),
                        html.Hr(),
                        html.Button(
                            id="save-button",
                            n_clicks=0,
                            children="現在のデータを保存",
                            className="bg-dark text-white setting_buttom",
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
    Input("delete-button", "n_clicks"),
    Input("shared-selected-df", "data"),
    State("col-dropdown", "value"),
    State("table", "data"),
)
def update_table(n, data, cols, table_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = "No clicks yet"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "shared-selected-df":
        df = pd.read_csv(data, low_memory=False)
        selectedfile = data.split("/")
        columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
        col_options = [{"label": i, "value": i} for i in df.columns]
        data = df.to_dict("records")
        print("aaa")
        print(data)
        return selectedfile[-1], data, columns, col_options

    elif trigger_id == "delete-button" and n > 0:
        df = pd.DataFrame(table_data).drop(columns=cols)
        selectedfile = data.split("/")
        columns = [{"name": i, "id": j} for i, j in zip(df, df.columns)]
        col_options = [{"label": i, "value": i} for i in df.columns]
        return (
            selectedfile[-1],
            df.to_dict("records"),
            columns,
            col_options,
        )
    else:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
