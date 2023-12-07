import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html

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
                            [html.H6(id="home-title")],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu ",
        ),
        dbc.Row(
            [
                html.Div(
                    dcc.Loading(
                        html.Div(id="home-graph1", className="bg-light"),
                        type="circle",
                    ),
                ),
            ],
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Loading(
                            html.Div(id="home-graph2", className="bg-light"),
                            type="circle",
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Loading(
                            html.Div(id="home-graph3", className="bg-light"),
                            type="circle",
                        ),
                    ]
                ),
            ],
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
                            "可視化",
                            style={
                                "margin-top": "8px",
                                "margin-bottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dbc.Button(
                            id="deaths",
                            n_clicks=0,
                            children="死亡者数に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="move-in",
                            n_clicks=0,
                            children="転出者数に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="○○に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="○○に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="○○に関して",
                            className=" text-white setting_button",
                            color="secondary",
                        ),
                        dbc.Button(
                            id="",
                            n_clicks=0,
                            children="○○に関して",
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
                    width=10,
                ),
            ]
        )
    ]
)


@callback(
    Output("home-title", "children", allow_duplicate=True),
    Output("home-graph1", "children", allow_duplicate=True),
    Output("home-graph2", "children", allow_duplicate=True),
    Output("home-graph3", "children", allow_duplicate=True),
    Input("deaths", "n_clicks"),
    State("shared-selected-df", "data"),
    prevent_initial_call=True,
)
def deaths_graph(n, data):
    if n > 0:
        df = pd.read_csv(data, low_memory=False)
        df = df[df["減事由コード"] == "B21"]
        df["死亡日"] = df["死亡日"].astype(str).str.slice(0, 4)
        df["死亡日"] = pd.to_datetime(df["死亡日"], format="%Y", errors="coerce")
        df["年"] = df["死亡日"].dt.year

        death_counts = df.groupby("年").size()
        gender_death_counts = df.groupby(["年", "性別名"]).size()
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=death_counts.index,
                y=death_counts.values,
                mode="lines",
                name="全体",
            )
        )
        for gender in gender_death_counts.index.get_level_values("性別名").unique():
            specific_gender_death_counts = gender_death_counts.xs(gender, level=1)
            fig1.add_trace(
                go.Scatter(
                    x=specific_gender_death_counts.index,
                    y=specific_gender_death_counts.values,
                    mode="lines",
                    name=gender,
                )
            )
        fig1.update_layout(title="性別ごとの死亡者数推移")

        city_death_counts = df.groupby(["年", "自治会コード名"]).size()
        fig2 = go.Figure()
        for city in city_death_counts.index.get_level_values("自治会コード名").unique():
            specific_city_death_counts = city_death_counts.xs(city, level=1)
            fig2.add_trace(
                go.Bar(
                    x=specific_city_death_counts.index,
                    y=specific_city_death_counts.values,
                    name=str(city),
                )
            )
        fig2.update_layout(barmode="stack", title="市町村別の死亡者数推移")

        title = "年ごとの死亡者数"
        return (title, dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), None)
    else:
        return html.Div("分析に適さないデータを選択しています")


@callback(
    Output("home-title", "children", allow_duplicate=True),
    Output("home-graph1", "children", allow_duplicate=True),
    Output("home-graph2", "children", allow_duplicate=True),
    Output("home-graph3", "children", allow_duplicate=True),
    Input("move-in", "n_clicks"),
    State("shared-selected-df", "data"),
    prevent_initial_call=True,
)
def move_graph(n, data):
    if n > 0:
        df = pd.read_csv(data, low_memory=False)
        df["住民減異動日"] = df["住民減異動日"].astype(str).str.slice(0, 4)
        df["住民増異動日"] = df["住民増異動日"].astype(str).str.slice(0, 4)

        df["転出年"] = pd.to_datetime(df["住民減異動日"], format="%Y", errors="coerce").dt.year
        df["転入年"] = pd.to_datetime(df["住民増異動日"], format="%Y", errors="coerce").dt.year

        df_out = df[
            (df["減事由コード"] == "B51")
            | (df["減事由コード"] == "B12")
            | (df["減事由コード"] == "B11")
            | (df["減事由コード"] == "B13")
        ]
        df_in = df[df["増事由コード"] == "A11"]

        in_counts = df_out.groupby("転入年").size()
        out_counts = df_out.groupby("転出年").size()

        print(out_counts)
        gender_out_counts = df_out.groupby(["転出年", "性別名"]).size()
        gender_in_counts = df_in.groupby(["転入年", "性別名"]).size()

        fig_out = go.Figure()
        for gender in gender_out_counts.index.get_level_values("性別名").unique():
            specific_gender_out_counts = gender_out_counts.xs(gender, level=1)
            fig_out.add_trace(
                go.Scatter(
                    x=specific_gender_out_counts.index,
                    y=specific_gender_out_counts.values,
                    mode="lines",
                    name=gender,
                )
            )

        fig_out.update_layout(title="年別性別別転出者数推移")

        fig_in = go.Figure()
        for gender in gender_in_counts.index.get_level_values("性別名").unique():
            specific_gender_in_counts = gender_in_counts.xs(gender, level=1)
            fig_in.add_trace(
                go.Scatter(
                    x=specific_gender_in_counts.index,
                    y=specific_gender_in_counts.values,
                    mode="lines",
                    name=gender,
                )
            )

        fig_in.update_layout(title="年別性別別転入者数推移")

        fig_inout = go.Figure()
        fig_inout.add_trace(
            go.Scatter(
                x=out_counts.index,
                y=out_counts.values,
                mode="lines",
                name="転出者数",
            )
        )
        fig_inout.add_trace(
            go.Scatter(
                x=in_counts.index,
                y=in_counts.values,
                mode="lines",
                name="転入者数",
            )
        )
        fig_inout.update_layout(title="年別の転入者数・転出者数推移")
        title = "年ごとの転出者数"
        return (
            title,
            dcc.Graph(figure=fig_in),
            dcc.Graph(figure=fig_out),
            dcc.Graph(figure=fig_inout),
        )
    else:
        return (
            html.Div("分析に適さないデータを選択しています"),
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
