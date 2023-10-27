import glob
import os

import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_uploader as du
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

df = pd.read_csv("data/data_sample.csv")
uploaded_files_dict = {}

vars_cat = [var for var in df.columns if var.startswith("cat")]
vars_cont = [var for var in df.columns if var.startswith("cont")]

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
app.title = "テストページ"
passPair = {"User1": "AAA", "User2": "BBB"}
auth = dash_auth.BasicAuth(app, passPair)
du.configure_upload(app, r"/usr/src/data")


# アプリケーションの初期化時にdataディレクトリをスキャン
for filepath in glob.glob("data/*/*"):
    filename = os.path.basename(filepath)
    uploaded_files_dict[filename] = filepath

sidebarToggleBtn = dmc.Button(
    children=[
        DashIconify(icon="ci:hamburger-lg", width=32, height=32, color="#c2c7d0")
    ],
    variant="subtle",
    p=1,
    id="sidebar-button",
)

sidebar = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5(
                            "データ分析ツール",
                        ),
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            [
                dbc.Container(
                    [
                        html.H4("Upload with Dash-uploader"),
                        du.Upload(
                            id="input",
                            max_file_size=1800,
                            filetypes=["csv"],
                            max_files=1,
                            cancel_button=True,
                        ),
                        html.P(id="input_info"),
                        html.Br(),
                        dcc.Dropdown(
                            id="uploaded-files-dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in uploaded_files_dict.keys()
                            ],  # アップロードされたファイルのリストがここに入ります
                            placeholder="Select a file",
                        ),
                        html.Button(
                            id="file-select-button",
                            n_clicks=0,
                            children="ファイル変更",
                            style={"margin-top": "16px"},
                            className="bg-dark text-white",
                        ),
                        html.Hr(),
                    ]
                )
            ],
            style={"height": "50vh", "margin": "8px"},
        ),
    ],
)

settings = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    sidebarToggleBtn,
                    width=1,
                    className="sidebarToggleBtn",
                ),
                dbc.Col(
                    html.H5(
                        "Settings",
                    ),
                    width=11,
                ),
            ],
            className="bg-primary text-white font-italic topMenu",
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
                            id="my-cat-picker",
                            multi=False,
                            value="cat0",
                            options=[{"label": x, "value": x} for x in vars_cat],
                            style={"width": "95%"},
                        ),
                        html.P(
                            "連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="my-cont-picker",
                            multi=False,
                            value="cont0",
                            options=[{"label": x, "value": x} for x in vars_cont],
                            style={"width": "95%"},
                        ),
                        html.P(
                            "相関行列の連続変数",
                            style={"margin-top": "16px", "margin-bottom": "4px"},
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="my-corr-picker",
                            multi=True,
                            value=vars_cont + ["target"],
                            options=[
                                {"label": x, "value": x} for x in vars_cont + ["target"]
                            ],
                            style={"width": "95%"},
                        ),
                        html.Button(
                            id="my-button",
                            n_clicks=0,
                            children="設定変更",
                            style={"margin-top": "16px"},
                            className="bg-dark text-white",
                        ),
                        html.Hr(),
                    ]
                )
            ],
            style={"height": "50vh", "margin": "8px"},
        ),
    ]
)

content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5(
                            "タイトルタイトルタイトルタイトル",
                        )
                    ],
                    className="title",
                ),
                dbc.Col(
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("More pages", header=True),
                            dbc.DropdownMenuItem("Page 2", href="#"),
                            dbc.DropdownMenuItem("Page 3", href="#"),
                        ],
                        label="分析方法の変更",
                    ),
                    className="changePageDropDown",
                ),
            ],
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(id="bar-title", className="font-weight-bold"),
                            dcc.Graph(id="bar-chart", className="bg-light"),
                        ]
                    ),
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.P(id="dist-title", className="font-weight-bold"),
                            dcc.Graph(id="dist-chart", className="bg-light"),
                        ]
                    ),
                    width=6,
                ),
            ],
            style={
                "margin-top": "16px",
                "margin-left": "8px",
                "margin-bottom": "8px",
                "margin-right": "8px",
            },
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        html.P(
                            "ヒートマップ",
                            className="font-weight-bold",
                        ),
                        dcc.Graph(id="corr-chart", className="bg-light"),
                    ]
                )
            ],
            style={"margin": "8px", "height": "100vh"},
        ),
    ],
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dcc.Location(id="url", refresh=False),
                dbc.Col(
                    [
                        dbc.Row(sidebar),
                    ],
                    className="bg-light",
                    width=2,
                    id="sidebar",
                ),
                dbc.Col(
                    [settings],
                    className="bg-light",
                    width=2,
                ),
                dbc.Col(
                    content,
                    id="content",
                    style={
                        "transition": "margin-left 0.3s ease-in-out",
                    },
                    width=8,
                ),
            ],
            justify="start",
        ),
    ],
    fluid=True,
)


# カテゴリー変数の分布の変数選択処理
@app.callback(
    Output("bar-chart", "figure"),
    Output("bar-title", "children"),
    [Input("my-button", "n_clicks"), Input("file-select-button", "n_clicks")],
    State("my-cat-picker", "value"),
)
def update_bar(n_clicks, file_n_clicks, cat_pick):
    bar_df = df.groupby(["target", cat_pick]).count()["id"].reset_index()
    bar_df["target"] = bar_df["target"].replace({0: "target=0", 1: "target=1"})

    fig_bar = px.bar(
        bar_df,
        x=cat_pick,
        y="id",
        color="target",
        color_discrete_sequence=["#bad6eb", "#2b7bba"],
    )

    fig_bar.update_layout(
        autosize=True,
        margin=dict(l=40, r=20, t=20, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title=None,
        yaxis_title=None,
        xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    title_bar = "カテゴリー変数の分布: " + cat_pick

    return fig_bar, title_bar


# 連続変数の分布の変数選択処理
@app.callback(
    Output("dist-chart", "figure"),
    Output("dist-title", "children"),
    [Input("my-button", "n_clicks"), Input("file-select-button", "n_clicks")],
    State("my-cont-picker", "value"),
)
def update_dist(n_clicks, file_n_clicks, cont_pick):
    num0 = df[df["target"] == 0][cont_pick].values.tolist()
    num1 = df[df["target"] == 1][cont_pick].values.tolist()

    fig_dist = ff.create_distplot(
        hist_data=[num0, num1],
        group_labels=["target=0", "target=1"],
        show_hist=False,
        colors=["#bad6eb", "#2b7bba"],
    )

    fig_dist.update_layout(
        autosize=True,
        margin=dict(t=20, b=20, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    title_dist = "連続変数の分布: " + cont_pick

    return fig_dist, title_dist


# ヒートマップの変数選択処理
@app.callback(
    Output("corr-chart", "figure"),
    [Input("my-button", "n_clicks"), Input("file-select-button", "n_clicks")],
    State("my-corr-picker", "value"),
)
def update_corr(n_clicks, file_n_clicks, corr_pick):
    df_corr = df[corr_pick].corr()
    x = list(df_corr.columns)
    y = list(df_corr.index)
    z = df_corr.values

    fig_corr = ff.create_annotated_heatmap(
        z,
        x=x,
        y=y,
        annotation_text=np.around(z, decimals=2),
        hoverinfo="z",
        colorscale="Blues",
    )

    fig_corr.update_layout(
        autosize=True,
        margin=dict(l=40, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig_corr


@app.callback(
    Output("sidebar", "style"),
    Output("content", "style"),
    Input("sidebar-button", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks):
    if n_clicks:
        if n_clicks % 2 == 1:  # toggle on odd clicks
            return (
                {"display": "none"},
                {
                    "marginLeft": "0px",
                    "transition": "margin-left 0.3s ease-in-out",
                    "width": "83.33333%",
                },
            )
        else:  # toggle on even clicks
            return (
                {"marginLeft": "0px"},
                {
                    "marginLeft": "0px",
                    "transition": "margin-left 0.3s ease-in-out",
                    "width": "66.66667%",
                },
            )
    raise PreventUpdate


@du.callback(
    output=Output("uploaded-files-dropdown", "options"),
    id="input",
)
def callback_on_completion(status: du.UploadStatus):
    for x in status.uploaded_files:
        filename = os.path.basename(str(x))
        uploaded_files_dict[filename] = str(x)
    uploaded_files = list(uploaded_files_dict.keys())
    return [{"label": i, "value": i} for i in uploaded_files]


@app.callback(
    Output("file-select-button", "n_clicks"),
    Input("uploaded-files-dropdown", "value"),
)
def reset_button_on_new_file(value):
    return 0


@app.callback(
    Output(
        "file-select-button", "children"
    ),  # ダミーの出力を 'my-button' の 'children' プロパティに変更
    Input("file-select-button", "n_clicks"),
    State("uploaded-files-dropdown", "value"),
)
def load_new_file(n_clicks, value):
    if n_clicks > 0:
        global df
        df = pd.read_csv(uploaded_files_dict[value])
    return "ファイル変更"


if __name__ == "__main__":
    app.run_server(port=5000, debug=True, host="0.0.0.0", use_reloader=True)
