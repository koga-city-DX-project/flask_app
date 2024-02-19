import glob

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

all_data_rate = {}

column_types = {
    "異動ＳＥＱ": int,
    "増異動日": int,
    "増事由コード名": str,
    "減異動日": int,
    "減事由コード名": "Int8",
    "最新異動日": int,
    "最新異動事由コード名": str,
    "性別": int,
    "性別名": str,
    "死亡日": str,
    "続柄": str,
    "続柄名": str,
    "住民となった異動日": int,
    "自治会コード": int,
    "自治会コード名": str,
    "小学校区コード": int,
    "小学校区コード名": str,
    "住民コード_conv": int,
    "世帯コード_conv": int,
    "生年月日_conv": str,
    "住所_conv": str,
    "生年月日_year": int,
    "要介護認定申請日": str,
    "二次判定要介護度": "Int64",
    "二次判定要介護度名": str,
    "要介護認定日": str,
    "認定開始日": str,
    "認定終了日": str,
    "認定状態": str,
}


def load_and_process_files():
    global all_data_rate
    files = glob.glob("/usr/src/data/save/認定状態・総人口20**.csv")
    all_data = []
    for file in files:
        year = file[-8:-4]  # ファイル名から年を抽出
        df = pd.read_csv(file, dtype=column_types)
        df = df.drop_duplicates(subset=["住民コード_conv"])
        columns_to_keep = [
            "住民コード_conv",
            "自治会コード",
            "自治会コード名",
            "小学校区コード",
            "小学校区コード名",
            "生年月日_year",
            "認定状態",
        ]
        year = file[-8:-4]  # ファイル名から年を抽出
        df = pd.read_csv(file, dtype=column_types)
        df = df.drop_duplicates(subset=["住民コード_conv"])
        df = df[columns_to_keep]
        df["年"] = year
        df["年"] = df["年"].astype(int)
        df["生年月日_year"] = pd.to_numeric(
            df["生年月日_year"], errors="coerce"
        ).astype("Int64")
        df["行政区"] = df["自治会コード名"].str.extract("(.*区)")
        df["小学校区"] = df["小学校区コード名"].str.extract("(.*小)")
        df["年齢"] = df["年"].astype(int) - df["生年月日_year"]
        late_elderly_data = df[df["年齢"] >= 76]
        df = df[df["年齢"] >= 66]  # 修正: 65歳未満のデータを削除
        all_data.append(df)
        # 全体のデータに対する集計
        overall_data_count = df.groupby("年").size()
        overall_late_elderly_count = late_elderly_data.groupby("年").size()
        overall_certified_count = df[df["認定状態"] == "認定済み"].groupby("年").size()
        overall_certified_rate = overall_certified_count / overall_data_count
        overall_late_elderly_rate = overall_late_elderly_count / overall_data_count

        # 行政区ごとの集計
        district_data_count = df.groupby("行政区").size()
        district_certified_count = (
            df[df["認定状態"] == "認定済み"].groupby("行政区").size()
        )
        district_elderly_count = late_elderly_data.groupby("行政区").size()
        district_certified_rate = district_certified_count / district_data_count
        district_elderly_rate = district_elderly_count / district_data_count

        # 小学校区ごとの集計
        school_data_count = df.groupby("小学校区").size()
        school_certified_count = (
            df[df["認定状態"] == "認定済み"].groupby("小学校区").size()
        )
        school_elderly_count = late_elderly_data.groupby("小学校区").size()
        school_certified_rate = school_certified_count / school_data_count
        school_elderly_rate = school_elderly_count / school_data_count

        # 集計結果を辞書に保存
        all_data_rate[year] = {
            "Total Certified Count": overall_certified_count.to_dict(),
            "Total Late Elderly Count": overall_late_elderly_count.to_dict(),
            "Total Certified Rate": overall_certified_rate.to_dict(),
            "Total Late Elderly Rate": overall_late_elderly_rate.to_dict(),
            "District Certified Count": district_certified_count.to_dict(),
            "District Elderly Count": district_elderly_count.to_dict(),
            "District Certified Rate": district_certified_rate.to_dict(),
            "District Elderly Rate": district_elderly_rate.to_dict(),
            "School Certified Count": school_certified_count.to_dict(),
            "School Elderly Count": school_elderly_count.to_dict(),
            "School Certified Rate": school_certified_rate.to_dict(),
            "School Elderly Rate": school_elderly_rate.to_dict(),
        }
    data = pd.concat(all_data)
    return data


data = load_and_process_files()


def district_option_set():
    data["自治会コード_str"] = data["自治会コード"].astype(str)
    district_to_code = {
        district: code[:2]
        for district, code in zip(data["行政区"], data["自治会コード_str"])
    }
    sorted_districts = sorted(
        data["行政区"].unique(), key=lambda x: district_to_code.get(x, "")
    )
    options = [{"label": district, "value": district} for district in sorted_districts]
    return options


def school_option_set():
    data["小学校区コード_str"] = data["小学校区コード"].astype(str)
    district_to_code = {
        district: code[:2]
        for district, code in zip(data["小学校区"], data["小学校区コード_str"])
    }
    sorted_districts = sorted(
        data["小学校区"].unique(), key=lambda x: district_to_code.get(x, "")
    )
    options = [{"label": district, "value": district} for district in sorted_districts]
    return options


def all_option_set():
    options = [{"label": "全体", "value": "全体"}]
    return options


dict_op = district_option_set()
scho_op = school_option_set()
all_op = all_option_set()


def overall_checked(fig, years, opt, val):
    if val == 1:
        certified_rates = [
            all_data_rate[year]["Total Certified Rate"] for year in years
        ]
    elif val == 2:
        certified_rates = [
            all_data_rate[year]["Total Certified Count"] for year in years
        ]
    c_rates = [list(rate.values())[0] for rate in certified_rates]
    fig.add_trace(
        go.Scatter(
            x=years,
            y=c_rates,
            mode="lines+markers",
            name=f"全体 要介護認定{opt}",
        )
    )


def elderly_graphview(fig, years, elderly_rates, ward, opt, val):
    if val == 1:
        fig.add_trace(
            go.Bar(
                x=years,
                y=elderly_rates,
                name=f"{ward} 後期高齢者{opt}",
                marker=dict(
                    color="lightblue",
                    line=dict(color="#333", width=2),
                ),
                opacity=0.5,  # 透明度の設定
            )
        )
        title = f"{ward}の要介護認定{opt}と後期高齢者{opt}の年次推移"
        ytitle = f"・後期高齢者{opt}"
    elif val > 1:
        title = f"行政区別の要介護認定{opt}の年次推移"
        ytitle = ""
    return title, ytitle


contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("要介護認定率・後期高齢者率出力")],
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
                    id="certification_rate_graph",
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
            ]
        ),
    ],
    style={"height": "100vh"},
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
                            "区別種類の選択",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="target_select",
                            options=[
                                {
                                    "label": "全体　認定率・後期高齢者比率(%)",
                                    "value": "全体P",
                                },
                                {
                                    "label": "全体　認定数・後期高齢者数(件)",
                                    "value": "全体C",
                                },
                                {
                                    "label": "行政区別　認定率・後期高齢者比率(%)",
                                    "value": "行政区別P",
                                },
                                {
                                    "label": "行政区別　認定数・後期高齢者数(件)",
                                    "value": "行政区別C",
                                },
                                {
                                    "label": "小学校区別　認定率・後期高齢者比率(%)",
                                    "value": "小学校区別P",
                                },
                                {
                                    "label": "小学校区別　認定数・後期高齢者数(件)",
                                    "value": "小学校区別C",
                                },
                            ],
                            value="全体P",
                            className="setting_dropdown",
                            placeholder="区別種類の選択",
                            clearable=False,
                            style={
                                "fontSize": "15px",
                            },
                        ),
                        html.P(
                            "表示区の絞り込み",
                            style={
                                "marginTop": "8px",
                                "marginBottom": "4px",
                            },
                            className="font-weight-bold",
                        ),
                        dcc.Dropdown(
                            id="ward_select",
                            className="setting_dropdown",
                            placeholder="表示区の絞り込み",
                        ),
                        dcc.Checklist(
                            id="overall_compare",
                            options=[{"label": "全体と比較する", "value": "c1"}],
                            className="option_P",
                        ),
                        dbc.Button(
                            href="#",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "25vh", "marginLeft": "1px"},
        ),
    ],
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
    Output("ward_select", "options"),
    Output("ward_select", "multi"),
    Output("ward_select", "value"),
    Input("target_select", "value"),
)
def update_menu(target_select):
    if target_select in ["行政区別P", "行政区別C"]:
        options = dict_op
        value = dict_op[0]["value"]
        multi = True
    elif target_select in ["小学校区別P", "小学校区別C"]:
        options = scho_op
        value = scho_op[0]["value"]
        multi = True
    elif target_select in ["全体P", "全体C"]:
        options = all_op
        value = all_op[0]["value"]
        multi = False
    return options, multi, value


@callback(
    Output("certification_rate_graph", "figure"),
    Input("target_select", "value"),
    Input("ward_select", "value"),
    Input("overall_compare", "value"),
)
def update_graph(target_select, ward_select, overall_compare):
    # グラフを動的に更新するロジック
    # 「全体」「行政区別」「小学校区別」の選択に応じて、異なるデータをグラフに反映させる
    global all_data_rate
    fig = go.Figure()
    ytitle = ""
    tform = ""
    years = sorted(all_data_rate.keys())  # 年度のリスト
    # 年度ごとにデータを抽出し、グラフを生成
    if target_select == "全体P" or target_select == "全体C":
        if target_select == "全体P":
            certified_rates = [
                all_data_rate[year]["Total Certified Rate"] for year in years
            ]
            elderly_rates = [
                all_data_rate[year]["Total Late Elderly Rate"] for year in years
            ]
            c_years = [list(rate.keys())[0] for rate in certified_rates]
            c_rates = [list(rate.values())[0] for rate in certified_rates]
            e_years = [list(rate.keys())[0] for rate in elderly_rates]
            e_rates = [list(rate.values())[0] for rate in elderly_rates]
            opt = "率(%)"
            tform = ".2%"
        elif target_select == "全体C":
            certified_rates = [
                all_data_rate[year]["Total Certified Count"] for year in years
            ]
            elderly_rates = [
                all_data_rate[year]["Total Late Elderly Count"] for year in years
            ]
            c_years = [list(rate.keys())[0] for rate in certified_rates]
            c_rates = [list(rate.values())[0] for rate in certified_rates]
            e_years = [list(rate.keys())[0] for rate in elderly_rates]
            e_rates = [list(rate.values())[0] for rate in elderly_rates]
            opt = "数(件)"
            tform = ""

        # 要介護認定率の折れ線グラフを追加
        fig.add_trace(
            go.Scatter(
                x=c_years,
                y=c_rates,
                mode="lines+markers",
                name=f"全体 要介護認定{opt}",
            )
        )
        # 後期高齢化率の縦棒グラフを追加
        fig.add_trace(
            go.Bar(
                x=e_years,
                y=e_rates,
                name=f"全体 後期高齢者{opt}",
                marker=dict(
                    color="lightblue",
                    line=dict(color="#333", width=2),
                ),
                opacity=0.5,  # 透明度の設定
            )
        )
        title = f"全体の要介護認定{opt}と後期高齢者{opt}の年次推移"

    elif target_select == "行政区別P" or target_select == "行政区別C":
        if isinstance(ward_select, str):
            ward_select = [ward_select]
        for ward in ward_select:
            if target_select == "行政区別P":
                certified_rates = [
                    all_data_rate[year]["District Certified Rate"].get(ward, 0)
                    for year in years
                ]
                elderly_rates = [
                    all_data_rate[year]["District Elderly Rate"].get(ward, 0)
                    for year in years
                ]
                opt = "率(%)"
                tform = ".2%"
            elif target_select == "行政区別C":
                certified_rates = [
                    all_data_rate[year]["District Certified Count"].get(ward, 0)
                    for year in years
                ]
                elderly_rates = [
                    all_data_rate[year]["District Elderly Count"].get(ward, 0)
                    for year in years
                ]
                opt = "数(件)"
                tform = ""
            fig.add_trace(
                go.Scatter(
                    x=years,  # 直接 years を使用
                    y=certified_rates,
                    mode="lines+markers",
                    name=f"{ward} 要介護認定{opt}",
                )
            )
        # 後期高齢化率の縦棒グラフを追加（複数選択時には表示しない）
        if len(ward_select) == 1:
            title, ytitle = elderly_graphview(fig, years, elderly_rates, ward, opt, 1)
        elif len(ward_select) > 1:
            title, ytitle = elderly_graphview(fig, years, elderly_rates, ward, opt, 2)
        # ここを消すな。全体の割合なのか総数なのかの判定を行っている。
        if overall_compare == ["c1"] and target_select == "行政区別P":
            overall_checked(fig, years, opt, 1)
        elif overall_compare == ["c1"] and target_select == "行政区別C":
            overall_checked(fig, years, opt, 2)

    elif target_select == "小学校区別P" or target_select == "小学校区別C":
        if isinstance(ward_select, str):
            ward_select = [ward_select]
        for ward in ward_select:
            if target_select == "小学校区別P":
                certified_rates = [
                    all_data_rate[year]["School Certified Rate"].get(ward, 0)
                    for year in years
                ]
                elderly_rates = [
                    all_data_rate[year]["School Elderly Rate"].get(ward, 0)
                    for year in years
                ]
                opt = "率(%)"
                tform = ".2%"
            elif target_select == "小学校区別C":
                certified_rates = [
                    all_data_rate[year]["School Certified Count"].get(ward, 0)
                    for year in years
                ]
                elderly_rates = [
                    all_data_rate[year]["School Elderly Count"].get(ward, 0)
                    for year in years
                ]
                opt = "数(件)"
                tform = ""
            fig.add_trace(
                go.Scatter(
                    x=years,  # 直接 years を使用
                    y=certified_rates,
                    mode="lines+markers",
                    name=f"{ward} 要介護認定{opt}",
                )
            )
        # 後期高齢化率の縦棒グラフを追加（複数選択時には表示しない）
        if len(ward_select) == 1:
            title, ytitle = elderly_graphview(fig, years, elderly_rates, ward, opt, 1)
        elif len(ward_select) > 1:
            title, ytitle = elderly_graphview(fig, years, elderly_rates, ward, opt, 2)
        # ここを消すな。全体の割合なのか総数なのかの判定を行っている。
        if overall_compare == ["c1"] and target_select == "小学校区別P":
            overall_checked(fig, years, opt, 1)
        elif overall_compare == ["c1"] and target_select == "小学校区別C":
            overall_checked(fig, years, opt, 2)

    fig.update_layout(
        title_text=title,
        title_font_size=24,
        xaxis=dict(title="年度", title_font=dict(size=20)),
        yaxis=dict(
            title=f"認定{opt}{ytitle}",
            title_font=dict(size=20),
            tickformat=tform,
        ),
        barmode="overlay",
    )

    return fig
