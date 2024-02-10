import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, callback, dcc, html

df_path = "/usr/src/data/save/Cause_Death_test.csv"


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
        {"label": "すべて" if category == "総数" else category, "value": category}
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
                            id="cause-death-comparison-type-dropdown",
                            options=[
                                {"label": "人数", "value": "people"},
                                {"label": "割合", "value": "rate"},
                            ],
                            value="people",
                            className="setting_dropdown",
                            placeholder="人数で比較",
                        ),
                        html.P("年齢", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="cause-death-age-dropdown",
                            options=[
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
                            placeholder="すべての地域を表示",
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
                            placeholder="すべての地域を表示",
                            multi=True,
                            className="setting_dropdown",
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
        Input("cause-death-comparison-type-dropdown", "value"),
        Input("cause-death-age-dropdown", "value"),
        Input("cause-death-sex-type-dropdown", "value"),
        Input("cause-death-category-dropdown", "value"),
        Input("cause-death-area-dropdown", "value"),
    ],
)
def update_cause_death_graph(comparison_type, ages, sexes, categories, areas):
    df = pd.read_csv(df_path)
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
                    if comparison_type == "rate":
                        y_data = (
                            df_area_category_sex_age[age]
                            / df_area_category_sex_age["総数(人)"]
                        )
                        y_title = "割合"
                    else:
                        y_data = df_area_category_sex_age[age]
                        y_title = "人数"
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

    fig.update_layout(
        title="死因別死亡者数の推移",
        title_font_size=24,
        xaxis=dict(title="年度", title_font=dict(size=20)),
        yaxis=dict(title=y_title, title_font=dict(size=20)),
        legend=dict(
            x=1.05,
            y=1,
        ),
    )

    return fig
