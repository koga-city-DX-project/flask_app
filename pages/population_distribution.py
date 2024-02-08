import colorsys

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, callback, dcc, html

df_path = "/usr/src/data/save/人口分布(国・福岡県・古賀市)test.csv"
contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("人口分布の推移(古賀市・福岡県・国)")],
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
                    id="aging_rate-graph",
                    style={"height": "80vh"},
                )
            ],
        ),
    ],
    style={"height": "100vh"},
)

settings = html.Div(
    children=[
        dbc.Row(
            dbc.Button(
                href="/select_populations",
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
                        html.P("比較方法", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-comparison-type-dropdown",
                            options=[
                                {"label": "人数", "value": "people"},
                                {"label": "割合", "value": "rate"},
                            ],
                            value="people",
                            className="setting_dropdown",
                            placeholder="人数で比較",
                        ),
                        html.P("年代", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-age-dropdown",
                            options=[
                                {"label": "0歳～4歳", "value": "0-4"},
                                {"label": "5歳～9歳", "value": "5-9"},
                                {"label": "10歳～14歳", "value": "10-14"},
                                {"label": "15歳～19歳", "value": "15-19"},
                                {"label": "20歳～24歳", "value": "20-24"},
                                {"label": "25歳～29歳", "value": "25-29"},
                                {"label": "30歳～34歳", "value": "30-34"},
                                {"label": "35歳～39歳", "value": "35-39"},
                                {"label": "40歳～44歳", "value": "40-44"},
                                {"label": "45歳～49歳", "value": "45-49"},
                                {"label": "50歳～54歳", "value": "50-54"},
                                {"label": "55歳～59歳", "value": "55-59"},
                                {"label": "60歳～64歳", "value": "60-64"},
                                {"label": "65歳～69歳", "value": "65-69"},
                                {"label": "70歳～74歳", "value": "70-74"},
                                {"label": "75歳～79歳", "value": "75-79"},
                                {"label": "80歳～84歳", "value": "80-84"},
                                {"label": "85歳～89歳", "value": "85-89"},
                                {"label": "90歳～94歳", "value": "90-94"},
                                {"label": "95歳～99歳", "value": "95-99"},
                                {"label": "100歳～", "value": "100-"},
                                {"label": "65歳～", "value": "65-"},
                                {"label": "総数", "value": "all"},
                            ],
                            value=["all"],
                            multi=True,
                            className="setting_dropdown",
                            placeholder="全年代の合計人数を表示",
                        ),
                        html.P("性別", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-sex-type-dropdown",
                            options=[
                                {"label": "男性", "value": "男性"},
                                {"label": "女性", "value": "女性"},
                                {"label": "男女計", "value": "男女計"},
                            ],
                            value=["男女計"],
                            multi=True,
                            className="setting_dropdown",
                            placeholder="男女合計人数を表示",
                        ),
                        html.P("比較地域", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-area-dropdown",
                            options=[
                                {"label": "古賀市", "value": "古賀市"},
                                {"label": "福岡県", "value": "福岡県"},
                                {"label": "国", "value": "国"},
                            ],
                            value=["古賀市", "福岡県", "国"],
                            placeholder="すべての地域を表示",
                            multi=True,
                            className="setting_dropdown",
                        ),
                        html.P("高齢化率", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="population-aging-rate-dropdown",
                            options=[
                                {"label": "表示", "value": "show"},
                                {"label": "非表示", "value": "hidden"},
                            ],
                            value="hidden",
                            className="setting_dropdown",
                        ),
                        dbc.Input(
                            id="population-file-name-input",
                            placeholder="ファイル名を入力",
                            type="text",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="population-file-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(id="population-modal-header"),
                                dbc.ModalBody(
                                    [
                                        html.Div(id="population-modal-text"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "ダウンロード",
                                                    id="population-download-confirm-button",
                                                    color="secondary",
                                                    className="me-2 bg-primary",
                                                ),
                                                dbc.Button(
                                                    "戻る",
                                                    id="population-cancel-button",
                                                    color="secondary",
                                                ),
                                            ],
                                            className="d-flex justify-content-center",
                                        ),
                                    ]
                                ),
                            ],
                            id="population-modal",
                            is_open=False,
                        ),
                        dcc.Download(id="download-population-distribution"),
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


def adjust_hue(hex_color, hue_factor):
    """指定されたHEXカラーの色相を調整します。"""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # RGBをHSVに変換し、色相（H）を調整
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h = (h + hue_factor) % 1
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    # RGBをHEXに戻す
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


# 性別と年齢層に基づく色の調整
def get_sex_age_color(base_color, sex, age):
    hue_factor = 0.1 if sex == "男性" else 0.2 if sex == "女性" else 0
    age_factor = {
        "0-4": 0.05,
        "5-9": 0.1,
        "10-14": 0.15,
        "all": 0,
        "65-": 0.2,
        "15-19": 0.05,
        "20-24": 0.1,
        "25-29": 0.15,
        "30-34": 0.2,
        "35-39": 0.05,
        "40-44": 0.1,
        "45-49": 0.15,
        "50-54": 0.2,
        "55-59": 0,
        "60-64": 0.05,
        "65-69": 0.1,
        "70-74": 0.15,
        "75-79": 0.2,
        "80-84": 0.0,
        "85-89": 0.05,
        "90-94": 0.1,
        "95-99": 0.15,
        "100-": 0.2,
    }.get(age, 0)
    return adjust_hue(base_color, hue_factor + age_factor)


@callback(
    Output("aging_rate-graph", "figure"),
    [
        Input("population-age-dropdown", "value"),
        Input("population-sex-type-dropdown", "value"),
        Input("population-area-dropdown", "value"),
        Input("population-aging-rate-dropdown", "value"),
        Input("population-comparison-type-dropdown", "value"),
    ],
)
def update_population_graph(ages, sexes, areas, aging_rate_visibility, comparison_type):
    df = pd.read_csv(df_path)
    age_columns = {
        "0-4": "0歳～4歳",
        "5-9": "5歳～9歳",
        "10-14": "10歳～14歳",
        "15-19": "15歳～19歳",
        "20-24": "20歳～24歳",
        "25-29": "25歳～29歳",
        "30-34": "30歳～34歳",
        "35-39": "35歳～39歳",
        "40-44": "40歳～44歳",
        "45-49": "45歳～49歳",
        "50-54": "50歳～54歳",
        "55-59": "55歳～59歳",
        "60-64": "60歳～64歳",
        "65-69": "65歳～69歳",
        "70-74": "70歳～74歳",
        "75-79": "75歳～79歳",
        "80-84": "80歳～84歳",
        "85-89": "85歳～89歳",
        "90-94": "90歳～94歳",
        "95-99": "95歳～99歳",
        "100-": "100歳以上",
        "all": "総数",
        "65-": "65歳以上",
    }
    area_line_styles = {"古賀市": "solid", "福岡県": "dot", "国": "dash"}
    colors = {"古賀市": "#1e00ff", "福岡県": "#ff0000", "国": "#1b941b"}
    if not ages:
        ages = ["all"]
    if not sexes:
        sexes = ["男女計"]
    if not areas:
        areas = ["古賀市", "福岡県", "国"]

    if not isinstance(ages, list):
        ages = [ages]
    if not isinstance(sexes, list):
        sexes = [sexes]
    if not isinstance(areas, list):
        areas = [areas]

    df_filtered = df[df["地域"].isin(areas) & df["性別"].isin(sexes)]

    fig = go.Figure()
    for area in areas:
        line_style = area_line_styles[area]
        for sex in sexes:
            for age in ages:
                color = get_sex_age_color(colors[area], sex, age)
                df_area_sex_age = df_filtered[
                    (df_filtered["地域"] == area) & (df_filtered["性別"] == sex)
                ]
                if comparison_type == "rate":
                    y_data = df_area_sex_age[age_columns[age]] / df_area_sex_age["総数"]
                else:
                    y_data = df_area_sex_age[age_columns[age]]
                fig.add_trace(
                    go.Scatter(
                        x=df_area_sex_age["年度"],
                        y=y_data,
                        mode="lines+markers",
                        name=f"{area} {sex} {age_columns[age]}",
                        line=dict(color=color, width=2, dash=line_style),
                        marker=dict(symbol="circle", size=8),
                    )
                )

        if aging_rate_visibility == "show":
            df_area = df_filtered[df_filtered["地域"] == area]
            fig.add_trace(
                go.Scatter(
                    x=df_area["年度"],
                    y=df_area["高齢化率"],
                    mode="lines",
                    name=f"{area} 高齢化率",
                    yaxis="y2",
                    line=dict(color=colors[area], width=3, dash="solid"),
                    showlegend=True,
                )
            )

    fig.update_layout(
        title="人口分布の推移",
        title_font_size=24,
        xaxis=dict(title="年度", title_font=dict(size=20)),
        yaxis=dict(title="人数", title_font=dict(size=20)),
        yaxis2=dict(
            title="高齢化率",
            title_font=dict(size=20),
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, 1],
            tickformat=".0%",
        ),
        legend_title="地域",
    )

    return fig


@callback(
    Output("download-population-distribution", "data"),
    [Input("care-lebel-download-button", "n_clicks")],
    [
        State("population-age-dropdown", "value"),
        State("population-sex-type-dropdown", "value"),
        State("population-area-dropdown", "value"),
        State("population-comparison-type-dropdown", "value"),
    ],
)
def generate_csv(
    n_clicks, selected_ages, selected_sexes, selected_areas, comparison_type
):
    if n_clicks is None:
        return dash.no_update
    return 0
