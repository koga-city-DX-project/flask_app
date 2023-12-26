import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

df_path = "/usr/src/data/save/介護認定管理.csv"
contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("介護度データ出力・分析")],
                            className="align-items-center",
                        )
                    ],
                ),
            ],
            className="bg-primary text-white font-italic topMenu ",
        ),
        dbc.Row(
            [
                dcc.Graph(
                    id="care-level-graph",
                    style={"height": "80vh"},
                )
            ],
        ),
        dbc.Row(dbc.Col(html.Div(""), style={"height": "20vh"})),
    ],
)

settings = html.Div(
    children=[
        dbc.Row(
            dbc.Button(
                href="/",
                children="戻る",
                className=" text-white back_button",
                external_link="true",
                color="dark",
            ),
            className="bg-primary text-white font-italic topMenu",
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        html.P(
                            "オプション",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "0",
                                "fontSize": "1.3em",
                            },
                            className="font-weight-bold",
                        ),
                        html.Hr(),
                        html.P(
                            "介護度別",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="care-level-rate-dropdown",
                            options=[
                                {"label": "すべて", "value": "k0"},
                                {"label": "要介護5", "value": "要介護５"},
                                {"label": "要介護4", "value": "要介護４"},
                                {"label": "要介護3", "value": "要介護３"},
                                {"label": "要介護2", "value": "要介護２"},
                                {"label": "要介護1", "value": "要介護１"},
                                {"label": "要支援2", "value": "要支援２"},
                                {"label": "要支援1", "value": "要支援１"},
                            ],
                            value="k0",
                            className="setting_dropdown",
                            placeholder="介護度別にみる",
                        ),
                        html.P("グラフの種類", className="font-weight-bold"),
                        dcc.Dropdown(
                            id="graph-type-dropdown",
                            options=[
                                {"label": "折れ線グラフ", "value": "line"},
                                {"label": "縦積み棒グラフ", "value": "stacked_bar"},
                            ],
                            value="line",
                            className="setting_dropdown",
                        ),
                        dbc.Button(
                            id="care-lebel-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dcc.Download(id="download-dataframe-csv"),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "20vh", "marginLeft": "1px"},
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


def process_data(file_path):
    df = pd.read_csv(file_path, usecols=["認定状態区分", "要介護認定日", "二次判定要介護度名", "二次判定要介護度"])
    df = df[df["認定状態区分"].isin([3, 5])]
    df = df[df["要介護認定日"] != "0"]
    df["要介護認定日"] = pd.to_datetime(df["要介護認定日"], format="%Y%m%d", errors="coerce")
    df["Year"] = df["要介護認定日"].dt.year
    return df


df = process_data(df_path)
color_map = {
    "要支援１": "blue",
    "要支援２": "lightblue",
    "要介護１": "green",
    "要介護２": "lightgreen",
    "要介護３": "yellow",
    "要介護４": "orange",
    "要介護５": "red",
    "非該当": "gray",
    "再調査": "gray",
    "経過的要介護": "gray",
}


@callback(
    Output("care-level-graph", "figure"),
    [Input("care-level-rate-dropdown", "value"), Input("graph-type-dropdown", "value")],
)
def update_graph(selected_care_level, selected_graph_type):
    if selected_graph_type == "line":
        certified_df = df[
            (df["認定状態区分"] == 3) & (~df["二次判定要介護度名"].isin(["非該当", "再調査", "経過的要介護"]))
        ]
        grouped_df = (
            certified_df.groupby(["Year", "二次判定要介護度名"]).size().reset_index(name="Count")
        )
        total_counts = (
            certified_df.groupby("Year").size().reset_index(name="TotalCount")
        )
        grouped_df = grouped_df.merge(total_counts, on="Year")
        grouped_df["Percentage"] = grouped_df["Count"] / grouped_df["TotalCount"] * 100
        fig = go.Figure()
        if selected_care_level != "k0":
            if selected_care_level in grouped_df["二次判定要介護度名"].unique():
                level_df = grouped_df[grouped_df["二次判定要介護度名"] == selected_care_level]
                fig.add_trace(
                    go.Scatter(
                        x=level_df["Year"],
                        y=level_df["Percentage"],
                        mode="lines",
                        name=selected_care_level,
                        line=dict(color=color_map[selected_care_level]),
                    )
                )
        else:
            for care_level, color in color_map.items():
                level_df = grouped_df[grouped_df["二次判定要介護度名"] == care_level]
                fig.add_trace(
                    go.Scatter(
                        x=level_df["Year"],
                        y=level_df["Percentage"],
                        mode="lines",
                        name=care_level,
                        line=dict(color=color),
                    )
                )
    elif selected_graph_type == "stacked_bar":
        certified_df = df[(df["認定状態区分"] == 3)]
        grouped_df = (
            certified_df.groupby(["Year", "二次判定要介護度名"]).size().reset_index(name="Count")
        )
        total_counts = (
            certified_df.groupby("Year").size().reset_index(name="TotalCount")
        )
        grouped_df = grouped_df.merge(total_counts, on="Year")
        grouped_df["Percentage"] = grouped_df["Count"] / grouped_df["TotalCount"] * 100
        fig = go.Figure()
        if selected_care_level != "k0":
            if selected_care_level in grouped_df["二次判定要介護度名"].unique():
                level_df = grouped_df[grouped_df["二次判定要介護度名"] == selected_care_level]
                fig.add_trace(
                    go.Bar(
                        x=level_df["Year"],
                        y=level_df["Percentage"],
                        name=selected_care_level,
                        marker=dict(color=color_map[selected_care_level]),
                    )
                )
        else:
            for care_level, color in color_map.items():
                level_df = grouped_df[grouped_df["二次判定要介護度名"] == care_level]
                fig.add_trace(
                    go.Bar(
                        x=level_df["Year"],
                        y=level_df["Percentage"],
                        name=care_level,
                        marker=dict(color=color),
                    )
                )
        fig.update_layout(barmode="stack")

    fig.update_layout(title="選択された要介護度の年次推移", xaxis_title="年度", yaxis_title="割合 (%)")

    return fig


@callback(
    Output("download-dataframe-csv", "data"),
    [Input("care-lebel-download-button", "n_clicks")],
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    return dcc.send_file("/usr/src/data/save/介護認定管理.csv")
