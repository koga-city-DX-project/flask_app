import base64
import math
import re

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, callback, dcc, html

df_path = "/usr/src/data/save/CauseDeath.csv"


def ensure_list(value, default_value):
    """指定された値がリストでない場合、リストに変換します。
    値が None または空の場合、デフォルト値をリストとして返します。

    :param value: 入力値（リスト、またはその他の値）
    :param default_value: デフォルト値
    :return: 値がリスト化された結果
    """
    if not value:
        return [default_value]
    elif not isinstance(value, list):
        return [value]
    return value


def legend_name(ages, age, sexes, sex, categories, category, areas, area):
    """
    オプションの値から凡例名を作成します。

    :param ages: 選択した年代のリスト
    :param age: 現在処理中の年代
    :param sexes: 選択した性別のリスト
    :param sex: 現在処理中の性別
    :param categories: 選択した分類のリスト
    :param category: 現在処理中の分類
    :param areas: 選択した地域のリスト
    :param area: 現在処理中の地域
    :return: 凡例名
    """
    parts = []
    if len(areas) > 1:
        parts.append(area)

    if len(categories) > 1:
        parts.append(category)

    if len(sexes) > 1 or (len(sexes) == 1 and sex != "男女計"):
        parts.append(sex)

    if len(ages) > 1 or (len(ages) == 1 and age != "総数(人)"):
        parts.append(age)
    legend_name = " ".join(parts)
    if legend_name == "":
        legend_name = f"{area}全体"
    return legend_name


def create_dropdown_options_from_csv(file_path, column_name):
    """
    CSVファイルから特定の列のユニークな値を読み込み、Dashのドロップダウンオプションリストを作成します。

    :param file_path: CSVファイルのパス
    :param column_name: 値を取得する列の名前
    :return: Dashのドロップダウンコンポーネントのオプションとして使用できる辞書のリスト
    """
    df = pd.read_csv(file_path)

    options = [
        {"label": "総数" if category == "総数" else category, "value": category}
        for category in df[column_name].unique()
    ]

    return options


dropdown_options = create_dropdown_options_from_csv(df_path, "分類")
contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("死因(古賀市・福岡県・国)")],
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
                    id="cause-death-graph",
                    style={"height": "80vh"},
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToAdd": [
                            "pan2d",
                            "autoScale2d",
                        ],
                        "modeBarButtonsToRemove": [
                            "zoomIn2d",
                            "zoomOut2d",
                            "select2d",
                            "lasso2d",
                            "toggleSpikelines",
                            "hoverClosestCartesian",
                            "hoverCompareCartesian",
                        ],
                    },
                ),
                html.Div(id="cause-death-zoom-range-store", style={"display": "none"}),
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
                        html.P("年齢", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-age-dropdown",
                            options=[
                                {"label": "10代", "value": "10代"},
                                {"label": "20代", "value": "20代"},
                                {"label": "30代", "value": "30代"},
                                {"label": "40代", "value": "40代"},
                                {"label": "50代", "value": "50代"},
                                {"label": "60代", "value": "60代"},
                                {"label": "70代", "value": "70代"},
                                {"label": "80代", "value": "80代"},
                                {"label": "90代", "value": "90代"},
                                {"label": "0歳～4歳", "value": "0歳～4歳"},
                                {"label": "5歳～9歳", "value": "5歳～9歳"},
                                {"label": "10歳～14歳", "value": "10歳～14歳"},
                                {"label": "15歳～19歳", "value": "15歳～19歳"},
                                {"label": "20歳～24歳", "value": "20歳～24歳"},
                                {"label": "25歳～29歳", "value": "25歳～29歳"},
                                {"label": "30歳～34歳", "value": "30歳～34歳"},
                                {"label": "35歳～39歳", "value": "35歳～39歳"},
                                {"label": "40歳～44歳", "value": "40歳～44歳"},
                                {"label": "45歳～49歳", "value": "45歳～49歳"},
                                {"label": "50歳～54歳", "value": "50歳～54歳"},
                                {"label": "55歳～59歳", "value": "55歳～59歳"},
                                {"label": "60歳～64歳", "value": "60歳～64歳"},
                                {"label": "65歳～69歳", "value": "65歳～69歳"},
                                {"label": "70歳～74歳", "value": "70歳～74歳"},
                                {"label": "75歳～79歳", "value": "75歳～79歳"},
                                {"label": "80歳～84歳", "value": "80歳～84歳"},
                                {"label": "85歳～89歳", "value": "85歳～89歳"},
                                {"label": "90歳～94歳", "value": "90歳～94歳"},
                                {"label": "95歳～99歳", "value": "95歳～99歳"},
                                {"label": "100歳～", "value": "100歳～"},
                                {"label": "総数(人)", "value": "総数(人)"},
                            ],
                            value=[],
                            className="setting_dropdown",
                            placeholder="全年代の合計人数を表示",
                            multi=True,
                        ),
                        html.P("性別", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-sex-type-dropdown",
                            options=[
                                {"label": "男性", "value": "男性"},
                                {"label": "女性", "value": "女性"},
                                {"label": "男女計", "value": "男女計"},
                            ],
                            value=[],
                            className="setting_dropdown",
                            placeholder="男女合計人数を表示",
                            multi=True,
                        ),
                        html.P("分類", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-category-dropdown",
                            options=dropdown_options,
                            value=[],
                            placeholder="全分類",
                            multi=True,
                            className="setting_dropdown",
                        ),
                        html.P("比較地域", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-area-dropdown",
                            options=[
                                {"label": "古賀市", "value": "古賀市"},
                                {"label": "福岡県", "value": "福岡県"},
                                {"label": "国", "value": "国"},
                            ],
                            value=["古賀市"],
                            placeholder="古賀市のみを表示",
                            multi=True,
                            className="setting_dropdown",
                        ),
                        dbc.Input(
                            id="cause-death-file-name-input",
                            placeholder="ファイル名を入力",
                            type="text",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="cause-death-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(id="cause-death-modal-header"),
                                dbc.ModalBody(
                                    [
                                        html.Div(id="cause-death-modal-text"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "ダウンロード",
                                                    id="cause-death-download-confirm-button",
                                                    color="secondary",
                                                    className="me-2 bg-primary",
                                                ),
                                                dbc.Button(
                                                    "戻る",
                                                    id="cause-death-download-cancel-button",
                                                    color="secondary",
                                                ),
                                            ],
                                            className="d-flex justify-content-center",
                                        ),
                                    ]
                                ),
                            ],
                            id="cause-death-modal",
                            is_open=False,
                        ),
                        dcc.Download(id="download-cause-death-data"),
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


@callback(
    Output("cause-death-graph", "figure"),
    [
        Input("cause-death-age-dropdown", "value"),
        Input("cause-death-sex-type-dropdown", "value"),
        Input("cause-death-category-dropdown", "value"),
        Input("cause-death-area-dropdown", "value"),
    ],
)
def update_cause_death_graph(ages, sexes, categories, areas):
    df = pd.read_csv(df_path)
    shown_legends = set()
    ages = ensure_list(ages, "総数(人)")
    sexes = ensure_list(sexes, "男女計")
    areas = ensure_list(areas, "古賀市")
    categories = ensure_list(categories, "総数")
    symbols = {"古賀市": "circle", "福岡県": "square", "国": "diamond"}
    line_styles = {"男性": "solid", "女性": "dot", "男女計": "solid"}
    widths = {"古賀市": 1, "福岡県": 2, "国": 3}
    df_filtered = df[
        df["地域"].isin(areas) & df["分類"].isin(categories) & df["性別"].isin(sexes)
    ]

    fig = go.Figure()

    for area in areas:
        symbol = symbols[area]
        for category in categories:
            for sex in sexes:
                line_style = line_styles[sex]
                for age in ages:
                    line_width = widths[area]
                    df_area_category_sex_age = df_filtered[
                        (df_filtered["地域"] == area)
                        & (df_filtered["性別"] == sex)
                        & (df_filtered["分類"] == category)
                    ]
                    y_data = df_area_category_sex_age[age]
                    y_title = "人数"
                    y_tickformat = None
                    graph_legend_name = legend_name(
                        ages, age, sexes, sex, categories, category, areas, area
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_area_category_sex_age["年度"],
                            y=y_data,
                            mode="lines+markers",
                            name=graph_legend_name,
                            line=dict(width=line_width, dash=line_style),
                            marker=dict(symbol=symbol, size=12),
                        )
                    )
    if (len(ages) + len(sexes) + len(areas)) <= 3:
        excluded_categories = [
            "ウイルス性肝炎",
            "悪性新生物",
            "心疾患",
            "総数",
            "脳血管疾患",
            "不慮の事故",
            "自殺",
        ]

        for year in df["年度"].unique():
            df_year = df[df["年度"] == year]
            for area in areas:
                df_area = df_year[df_year["地域"] == area]
                for sex in sexes:
                    df_sex = df_area[df_area["性別"] == sex]
                    for age in ages:
                        if categories == ["総数"]:
                            df_filtered = (
                                df_sex.groupby(["分類"])[age].sum().reset_index()
                            )
                            df_summary = df_filtered[
                                ~df_filtered["分類"].isin(excluded_categories)
                                & (df_filtered[age] > 0)
                            ]
                            total_deaths = df_sex[df_sex["分類"] == "総数"][age].sum()

                            top_categories = df_summary.sort_values(
                                by=age, ascending=False
                            ).head(5)
                            top_categories_sorted = top_categories[
                                top_categories[age] > 0
                            ].sort_values(by=age, ascending=True)
                            top_sum = top_categories[age].sum()

                            other_sum = total_deaths - top_sum
                            if other_sum > 0:
                                fig.add_trace(
                                    go.Bar(
                                        x=[year],
                                        y=[other_sum],
                                        name="その他",
                                        marker=dict(color="grey"),
                                        opacity=0.7,
                                        showlegend="その他" not in shown_legends,
                                    )
                                )
                                shown_legends.add("その他")

                            for _, row in top_categories_sorted.iterrows():
                                category = row["分類"]
                                showlegend = category not in shown_legends
                                shown_legends.add(category)
                                fig.add_trace(
                                    go.Bar(
                                        x=[year],
                                        y=[row[age]],
                                        name=category,
                                        marker=dict(
                                            color=category_color_mapping.get(
                                                category, "grey"
                                            )
                                        ),
                                        opacity=0.7,
                                        showlegend=showlegend,
                                    )
                                )
                        elif len(categories) == 1:
                            category = categories[0]
                            df_filtered = df_sex[df_sex["分類"].isin(categories)]
                            age_columns = [
                                "10代",
                                "20代",
                                "30代",
                                "40代",
                                "60代",
                                "50代",
                                "70代",
                                "80代",
                                "90代",
                                "100歳以上",
                            ]
                            if year == 2017:
                                add_dummy_traces_for_legend(fig, age_columns)
                            add_stacked_bar_traces(fig, df_filtered, age_columns)

    fig.update_layout(
        barmode="stack",
        title="死因別死亡者数の推移",
        title_font_size=24,
        xaxis=dict(title="年度", title_font=dict(size=20)),
        yaxis=dict(
            title=y_title,
            title_font=dict(size=20),
            tickformat=y_tickformat,
        ),
        legend=dict(
            x=1.05,
            y=1,
        ),
        hovermode="x unified",
    )

    return fig


def add_dummy_traces_for_legend(fig, age_columns):
    for age in age_columns:
        fig.add_trace(
            go.Bar(
                x=[None],
                y=[None],
                name=age,
                marker=dict(color=age_color_mapping[age]),
                showlegend=True,
                hoverinfo="none",
            )
        )


def add_stacked_bar_traces(fig, df_filtered, age_columns):
    for age_column in age_columns:
        y_data = df_filtered[age_column]
        if y_data.sum() > 0:
            fig.add_trace(
                go.Bar(
                    x=df_filtered["年度"],
                    y=y_data,
                    name=age_column,
                    marker_color=age_color_mapping[age_column],
                    opacity=0.7,
                    showlegend=False,
                )
            )


@callback(
    [
        Output("cause-death-modal", "is_open"),
        Output("cause-death-modal-header", "children"),
        Output("cause-death-modal-text", "children"),
    ],
    [
        Input("cause-death-download-button", "n_clicks"),
        Input("cause-death-download-cancel-button", "n_clicks"),
        Input("cause-death-download-confirm-button", "n_clicks"),
    ],
    [
        State("cause-death-modal", "is_open"),
        State("cause-death-sex-type-dropdown", "value"),
        State("cause-death-category-dropdown", "value"),
        State("cause-death-area-dropdown", "value"),
        State("cause-death-file-name-input", "value"),
        State("cause-death-zoom-range-store", "children"),
    ],
)
def toggle_modal(
    n_open,
    n_cancel,
    n_download,
    is_open,
    sexes,
    categories,
    areas,
    file_name,
    zoom_range,
):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    sexes_text = ", ".join(sexes) if sexes else "男性,女性,男女計"
    categories_text = ", ".join(categories) if categories else "すべての分類"
    areas_text = ", ".join(areas) if areas else "古賀市"
    file_name = re.sub(r"[\s　]+", "", file_name) if file_name else ""
    if file_name is None or file_name == "":
        file_name = "cause_death.csv(※ファイル名未入力時)"
    else:
        file_name = f"{file_name}.csv"
    if zoom_range:
        start_year = math.ceil(zoom_range[0])
        end_year = math.floor(zoom_range[1])
        year_text = f"{start_year}年 - {end_year}年"
    else:
        year_text = "すべての年度"
    modal_body_text = [
        html.Div("ファイル名"),
        html.P(file_name),
        html.Div("選択性別"),
        html.P(sexes_text),
        html.Div(
            [
                html.Div("選択分類"),
                html.P(categories_text),
            ]
        ),
        html.Div(
            [
                html.Div("選択地域"),
                html.P(areas_text),
            ]
        ),
        html.Div("選択年度"),
        html.P(year_text),
    ]

    if button_id == "cause-death-download-button":
        return True, "ファイルの出力", modal_body_text
    elif button_id in [
        "cause-death-download-cancel-button",
        "cause-death-download-confirm-button",
    ]:
        return False, "", modal_body_text
    return is_open, "", modal_body_text


@callback(
    Output("download-cause-death-data", "data"),
    [Input("cause-death-download-confirm-button", "n_clicks")],
    [
        State("cause-death-sex-type-dropdown", "value"),
        State("cause-death-category-dropdown", "value"),
        State("cause-death-area-dropdown", "value"),
        State("cause-death-file-name-input", "value"),
        State("cause-death-zoom-range-store", "children"),
    ],
    prevent_initial_call=True,
)
def download_file(n_clicks, sexes, categories, areas, file_name, zoom_range):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "cause-death-download-confirm-button":
        filepath = "/usr/src/data/save/CauseDeath.csv"
        df = pd.read_csv(filepath)
        df_filtered = filter_df(df, sexes, categories, areas, zoom_range)
        if file_name is None or file_name == "":
            file_name = "cause_death"
        df_filtered = df_filtered.to_csv(index=False)
        b64 = base64.b64encode(df_filtered.encode("CP932")).decode("CP932")
        return dict(content=b64, filename=f"{file_name}.csv", base64=True)
    return dash.no_update


@callback(
    Output("cause-death-zoom-range-store", "children"),
    [
        Input("cause-death-graph", "relayoutData"),
        Input("cause-death-age-dropdown", "value"),
        Input("cause-death-sex-type-dropdown", "value"),
        Input("cause-death-category-dropdown", "value"),
        Input("cause-death-area-dropdown", "value"),
    ],
)
def update_zoom_range_store(
    relayoutData,
    age,
    sex,
    category,
    area,
):
    if not relayoutData:
        return dash.no_update
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if (
        button_id == "cause-death-age-dropdown"
        or button_id == "cause-death-sex-type-dropdown"
        or button_id == "cause-death-category-dropdown"
        or button_id == "cause-death-area-dropdown"
    ):
        return None
    if "xaxis.autorange" in relayoutData or "yaxis.autorange" in relayoutData:
        return None
    if ("yaxis.range[0]" in relayoutData or "yaxis.range[1]" in relayoutData) and (
        "xaxis.range[0]" not in relayoutData or "xaxis.range[1]" not in relayoutData
    ):
        return dash.no_update
    if (
        relayoutData
        and "xaxis.range[0]" in relayoutData
        and "xaxis.range[1]" in relayoutData
    ):
        return [relayoutData["xaxis.range[0]"], relayoutData["xaxis.range[1]"]]
    return dash.no_update


def filter_df(df, sexes, categories, areas, zoom_range):
    if areas is None or areas == []:
        areas = ["古賀市"]
    if sexes is None or sexes == []:
        sexes = ["男性", "女性", "男女計"]

    df_filtered = df[df["地域"].isin(areas)]
    if categories != []:
        df_filtered = df_filtered[df_filtered["分類"].isin(categories)]
    df_filtered = df_filtered[df_filtered["性別"].isin(sexes)]

    if zoom_range:
        df_filtered = df_filtered[
            (df_filtered["年度"] >= float(zoom_range[0]))
            & (df_filtered["年度"] <= float(zoom_range[1]))
        ]
    return df_filtered


age_color_mapping = {
    "10代": "#e377c2",  # ピンク
    "20代": "#7f7f7f",  # グレー
    "30代": "#2ca02c",  # 緑
    "40代": "#d62728",  # 赤
    "50代": "#9467bd",  # 紫
    "60代": "#8c564b",  # ブラウン
    "70代": "#1f77b4",  # 青
    "80代": "#ff7f0e",  # オレンジ
    "90代": "#bcbd22",  # ライム
    "100歳以上": "#17becf",  # シアン
}

category_color_mapping = {
    "腸管感染症": "#1f77b4",
    "結核": "#aec7e8",
    "敗血病": "#ff7f0e",
    "Ｂ型ウイルス性肝炎": "#ffbb78",
    "Ｃ型ウイルス性肝炎": "#2ca02c",
    "ヒト免疫不全ウイルス病": "#98df8a",
    "口唇，口腔及び咽頭の悪性新生": "#d62728",
    "食道の悪性新生物": "#ff9896",
    "胃の悪性新生物": "#8820e6",
    "結腸の悪性新生物": "#a683d4",
    "直腸Ｓ状結腸移行部及び直腸の悪性新生物": "#8c564b",
    "肝及び肝内胆管の悪性新生物": "#c49c94",
    "胆のう及びその他の胆道の悪性新生物": "#eb6e21",
    "膵の悪性新生物": "#f7b6d2",
    "喉頭の悪性新生物": "#7f7f7f",
    "気管，気管支及び肺の悪性新生物": "green",
    "皮膚の悪性新生物": "#bcbd22",
    "乳房の悪性新生物": "#dbdb8d",
    "子宮の悪性新生物": "#17becf",
    "卵巣の悪性新生物": "#9edae5",
    "前立腺の悪性新生物": "#393b79",
    "膀胱の悪性新生物": "#5254a3",
    "中枢神経系の悪性新生物": "#5c61ff",
    "悪性リンパ腫": "#9c9ede",
    "白血病": "#637939",
    "貧血": "#8ca252",
    "糖尿病": "#b5cf6b",
    "血管性及び詳細不明の認知症": "#cedb9c",
    "髄膜炎": "#8c6d31",
    "脊椎性筋縮症及び関連症候群": "#bd9e39",
    "パーキンソン病": "#e7ba52",
    "アルツハイマー病": "#e7cb94",
    "高血圧性疾患": "#843c39",
    "慢性リウマチ性心疾患": "#ad494a",
    "急性心筋梗塞": "#d6616b",
    "慢性非リウマチ性心内膜疾患": "#e7969c",
    "心筋症": "#7b4173",
    "不整脈及び伝導障害": "#a55194",
    "心不全": "#8c6d31",
    "脳血管疾患": "#de9ed6",
    "くも膜下出血": "#3182bd",
    "脳内出血": "#6baed6",
    "脳梗塞": "#9ecae1",
    "大動脈癌及び解離": "blue",
    "インフルエンザ": "#e6550d",
    "肺炎": "#fd8d3c",
    "急性気管支炎": "#fdae6b",
    "慢性閉塞性肺疾患": "#fdd0a2",
    "喘息": "#31a354",
    "胃潰瘍及び十二指腸潰瘍": "#74c476",
    "ヘルニア及び腸閉塞": "#a1d99b",
    "肝疾患": "#c7e9c0",
    "糸球体疾患及び腎尿細管間質性疾患": "#756bb1",
    "腎不全": "#9e9ac8",
    "妊娠期間及び胎児発育に関連する障害": "#bcbddc",
    "周産期に特異的な呼吸障害及び心血管障害": "#dadaeb",
    "周産期に特異的な感染症": "#636363",
    "胎児及び新生児の出血性障害及び血液障害": "#969696",
    "神経系の先天奇形": "#bdbdbd",
    "循環器系の先天奇形": "#d9d9d9",
    "消化器系の先天奇形": "#f7f7f7",
    "老衰": "#ff0000",  # 明るく鮮やかな赤色で老衰を強調
    "乳幼児突然死症候群": "#00ff00",  # 明るい緑色
    "不慮の事故": "#0000ff",  # 明るい青色
    "交通事故": "#00ffff",  # シアン
    "転倒・転落・墜落": "#ff00ff",  # マゼンタ
    "不慮の溺死及び溺水": "#ffff00",  # イエロー
    "自殺": "#7d0000",  # コーラル
}
