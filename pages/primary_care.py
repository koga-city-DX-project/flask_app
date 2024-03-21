import base64
import glob
import math
import re

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html

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
    print("認定率・後期高齢者率のデータを作成中")
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
        early_elderly_data = df[(df["年齢"] >= 66) & (df["年齢"] < 76)]
        df = df[df["年齢"] >= 66]  # 修正: 65歳未満のデータを削除
        all_data.append(df)
        # 全体のデータに対する集計
        overall_data_count = df.groupby("年").size()
        overall_late_elderly_count = late_elderly_data.groupby("年").size()
        overall_early_elderly_count = early_elderly_data.groupby("年").size()
        overall_certified_count = df[df["認定状態"] == "認定済み"].groupby("年").size()
        overall_certified_rate = overall_certified_count / overall_data_count
        overall_late_elderly_rate = overall_late_elderly_count / overall_data_count
        overall_early_elderly_rate = overall_early_elderly_count / overall_data_count

        # 行政区ごとの集計
        district_data_count = df.groupby("行政区").size()
        district_certified_count = (
            df[df["認定状態"] == "認定済み"].groupby("行政区").size()
        )
        district_elderly_count = late_elderly_data.groupby("行政区").size()
        district_early_elderly_count = early_elderly_data.groupby("行政区").size()
        district_certified_rate = district_certified_count / district_data_count
        district_elderly_rate = district_elderly_count / district_data_count
        district_early_elderly_rate = district_early_elderly_count / district_data_count

        # 小学校区ごとの集計
        school_data_count = df.groupby("小学校区").size()
        school_certified_count = (
            df[df["認定状態"] == "認定済み"].groupby("小学校区").size()
        )
        school_elderly_count = late_elderly_data.groupby("小学校区").size()
        school_early_elderly_count = early_elderly_data.groupby("小学校区").size()
        school_certified_rate = school_certified_count / school_data_count
        school_elderly_rate = school_elderly_count / school_data_count
        school_early_elderly_rate = school_early_elderly_count / district_data_count

        # 集計結果を辞書に保存
        all_data_rate[year] = {
            "Total Certified Count": overall_certified_count.to_dict(),
            "Total Late Elderly Count": overall_late_elderly_count.to_dict(),
            "Total Early Elderly Count": overall_early_elderly_count.to_dict(),
            "Total Certified Rate": overall_certified_rate.to_dict(),
            "Total Late Elderly Rate": overall_late_elderly_rate.to_dict(),
            "Total Early Elderly Rate": overall_early_elderly_rate.to_dict(),
            "District Certified Count": district_certified_count.to_dict(),
            "District Elderly Count": district_elderly_count.to_dict(),
            "District Early Elderly Count": district_early_elderly_count.to_dict(),
            "District Certified Rate": district_certified_rate.to_dict(),
            "District Elderly Rate": district_elderly_rate.to_dict(),
            "District Early Elderly Rate": district_early_elderly_rate.to_dict(),
            "School Certified Count": school_certified_count.to_dict(),
            "School Elderly Count": school_elderly_count.to_dict(),
            "School Early Elderly Count": school_early_elderly_count.to_dict(),
            "School Certified Rate": school_certified_rate.to_dict(),
            "School Elderly Rate": school_elderly_rate.to_dict(),
            "School Early Elderly Rate": school_early_elderly_rate.to_dict(),
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


def elderly_graphview(
    fig,
    years,
    elderly_rates,
    early_elderly_rates,
    ward,
    opt,
    val,
    col,
    rev_col,
    offset,
    width,
    base,
):
    if val == 1:
        fig.add_trace(
            go.Bar(
                x=years,
                y=elderly_rates,
                name=f"{ward} 後期高齢者{opt}",
                marker=dict(
                    color=col,
                    opacity=0.3,
                ),
                offset=offset,
                width=width,
                base=base,
                opacity=0.7,  # 透明度の設定
            )
        )
        new_base = elderly_rates.copy()
        if base != None:
            base = new_base
        fig.add_trace(
            go.Bar(
                x=years,
                y=early_elderly_rates,
                name=f"{ward} 前期高齢者{opt}",
                marker=dict(
                    color=rev_col,
                    opacity=0.3,
                ),
                offset=offset,
                width=width,
                base=base,
                opacity=0.7,  # 透明度の設定
            )
        )
        print(early_elderly_rates)
        title = f"{ward}の要介護認定{opt}と後期高齢者{opt}、前期高齢者{opt}の年次推移"
        ytitle = f"・後期高齢者{opt}"
    elif val > 1:
        title = f"各区別の要介護認定{opt}の年次推移"
        ytitle = ""
    return title, ytitle


def create_data_to_export():
    print("認定率・後期高齢者率の出力用データ作成中")
    export_data = [
        [
            "年度",
            "区別種類",
            "区名",
            "要介護認定数",
            "後期高齢者数",
            "要介護認定率",
            "後期高齢者率",
        ]
    ]

    years = sorted(all_data_rate.keys())

    for year in years:
        data = all_data_rate.get(year, {})
        total_certified_count = data.get("Total Certified Count")
        total_elderly_count = data.get("Total Late Elderly Count")
        total_certified_rate = data.get("Total Certified Rate")
        total_elderly_rate = data.get("Total Late Elderly Rate")
        total_certified_count = list(total_certified_count.values())[0]
        total_elderly_count = list(total_elderly_count.values())[0]
        total_certified_rate = list(total_certified_rate.values())[0]
        total_elderly_rate = list(total_elderly_rate.values())[0]

        export_data.append(
            [
                year,
                "全体",
                "全体",
                total_certified_count,
                total_elderly_count,
                total_certified_rate,
                total_elderly_rate,
            ]
        )

        for district, count in data.get("District Certified Count", {}).items():
            elderly_count = data.get("District Elderly Count", {}).get(district, 0)
            rate = data.get("District Certified Rate", {}).get(district, 0)
            elderly_rate = data.get("District Elderly Rate", {}).get(district, 0)
            export_data.append(
                [year, "行政区", district, count, elderly_count, rate, elderly_rate]
            )

        for school, count in data.get("School Certified Count", {}).items():
            elderly_count = data.get("School Elderly Count", {}).get(school, 0)
            rate = data.get("School Certified Rate", {}).get(school, 0)
            elderly_rate = data.get("School Elderly Rate", {}).get(school, 0)
            export_data.append(
                [year, "小学校区", school, count, elderly_count, rate, elderly_rate]
            )

    df_export_data = pd.DataFrame(export_data[1:], columns=export_data[0])
    filepath = "/usr/src/data/save/20240221primary_care.csv"
    df_export_data.to_csv(filepath, index=False)


create_data_to_export()

custom_colors = [
    "blue",  # 濃い青
    "#ff0000",  # 濃い赤
    "green",  # 濃い緑
    "#9467bd",  # 濃い紫
    "#8c564b",  # 濃い茶色
    "#e377c2",  # 濃いピンク
    "gray",  # 濃いグレー
    "#bcbd22",  # 濃い黄緑
    "#17becf",  # 濃いシアン
    "#ff6600",  # 濃いオレンジ
]

reverse_colors = [
    "#ff6600",  # 濃いオレンジ
    "#17becf",  # 濃いシアン
    "#bcbd22",  # 濃い黄緑
    "gray",  # 濃いグレー
    "#e377c2",  # 濃いピンク
    "#8c564b",  # 濃い茶色
    "#9467bd",  # 濃い紫
    "green",  # 濃い緑
    "#ff0000",  # 濃い赤
    "blue",  # 濃い青
]

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
                html.Div(id="primary-care-zoom-range-store", style={"display": "none"}),
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
                            placeholder="表示する区を選択してください",
                        ),
                        dcc.Checklist(
                            id="overall_compare",
                            options=[{"label": "全体と比較する", "value": "c1"}],
                            className="option_P",
                        ),
                        dbc.Input(
                            id="primary-care-file-name-input",
                            placeholder="ファイル名を入力",
                            type="text",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="primary-care-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(id="primary-care-modal-header"),
                                dbc.ModalBody(
                                    [
                                        html.Div(id="primary-care-modal-text"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "ダウンロード",
                                                    id="primary-care-download-confirm-button",
                                                    color="secondary",
                                                    className="me-2 bg-primary",
                                                ),
                                                dbc.Button(
                                                    "戻る",
                                                    id="primary-care-cancel-button",
                                                    color="secondary",
                                                ),
                                            ],
                                            className="d-flex justify-content-center",
                                        ),
                                    ]
                                ),
                            ],
                            id="primary-care-modal",
                            is_open=False,
                        ),
                        dcc.Download(id="download-primary-care"),
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
            early_elderly_rates = [
                all_data_rate[year]["Total Early Elderly Rate"] for year in years
            ]
            c_years = [list(rate.keys())[0] for rate in certified_rates]
            c_rates = [list(rate.values())[0] for rate in certified_rates]
            e_years = [list(rate.keys())[0] for rate in elderly_rates]
            e_rates = [list(rate.values())[0] for rate in elderly_rates]
            ea_years = [list(rate.keys())[0] for rate in early_elderly_rates]
            ea_rates = [list(rate.values())[0] for rate in early_elderly_rates]
            opt = "率(%)"
            tform = ".2%"
        elif target_select == "全体C":
            certified_count = [
                all_data_rate[year]["Total Certified Count"] for year in years
            ]
            elderly_count = [
                all_data_rate[year]["Total Late Elderly Count"] for year in years
            ]
            early_elderly_count = [
                all_data_rate[year]["Total Early Elderly Count"] for year in years
            ]
            c_years = [list(rate.keys())[0] for rate in certified_count]
            c_rates = [list(rate.values())[0] for rate in certified_count]
            e_years = [list(rate.keys())[0] for rate in elderly_count]
            e_rates = [list(rate.values())[0] for rate in elderly_count]
            ea_years = [list(rate.keys())[0] for rate in early_elderly_count]
            ea_rates = [list(rate.values())[0] for rate in early_elderly_count]
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
        # 後期高齢化率の縦棒グラフを 追加
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
        if len(ward_select) == 2:
            base = 0
            ward_offset_mapping = {ward_select[0]: -0.4, ward_select[1]: 0}
            ward_base_mapping = {ward_select[0]: None, ward_select[1]: base}
        for i, ward in enumerate(ward_select):
            color = custom_colors[i % len(custom_colors)]
            rev_color = reverse_colors[i % len(custom_colors)]
            if len(ward_select) == 2:
                offset = ward_offset_mapping.get(ward, 0)
                base = ward_base_mapping.get(ward, 0)
                width = 0.4
            else:
                offset = 0
                base = None
                width = 0.8
            if target_select == "行政区別P":
                certified_rates = [
                    all_data_rate[year]["District Certified Rate"].get(ward, 0)
                    for year in years
                ]
                elderly_rates = [
                    all_data_rate[year]["District Elderly Rate"].get(ward, 0)
                    for year in years
                ]
                early_elderly_rates = [
                    all_data_rate[year]["District Early Elderly Rate"].get(ward, 0)
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
                early_elderly_rates = [
                    all_data_rate[year]["District Early Elderly Count"].get(ward, 0)
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
                    line=dict(color=color),
                )
            )
            if len(ward_select) <= 2:
                title, ytitle = elderly_graphview(
                    fig,
                    years,
                    elderly_rates,
                    early_elderly_rates,
                    ward,
                    opt,
                    1,
                    color,
                    rev_color,
                    offset,
                    width,
                    base,
                )
            elif len(ward_select) > 2:
                title, ytitle = elderly_graphview(
                    fig,
                    years,
                    elderly_rates,
                    early_elderly_rates,
                    ward,
                    opt,
                    2,
                    color,
                    rev_color,
                    offset,
                    width,
                    base,
                )
        # ここを消すな。全体の割合なのか総数なのかの判定を行っている。
        if overall_compare == ["c1"] and target_select == "行政区別P":
            overall_checked(fig, years, opt, 1)
        elif overall_compare == ["c1"] and target_select == "行政区別C":
            overall_checked(fig, years, opt, 2)

    elif target_select == "小学校区別P" or target_select == "小学校区別C":
        if isinstance(ward_select, str):
            ward_select = [ward_select]
        if len(ward_select) == 2:
            base = 0
            ward_offset_mapping = {ward_select[0]: -0.4, ward_select[1]: 0}
            ward_base_mapping = {ward_select[0]: None, ward_select[1]: base}
        for i, ward in enumerate(ward_select):
            color = custom_colors[i % len(custom_colors)]
            rev_color = reverse_colors[i % len(custom_colors)]
            if len(ward_select) == 2:
                offset = ward_offset_mapping.get(ward, 0)
                base = ward_base_mapping.get(ward, 0)
                width = 0.4
            else:
                offset = 0
                base = None
                width = 0.8
            if target_select == "小学校区別P":
                certified_rates = [
                    all_data_rate[year]["School Certified Rate"].get(ward, 0)
                    for year in years
                ]
                elderly_rates = [
                    all_data_rate[year]["School Elderly Rate"].get(ward, 0)
                    for year in years
                ]
                early_elderly_rates = [
                    all_data_rate[year]["School Early Elderly Rate"].get(ward, 0)
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
                early_elderly_rates = [
                    all_data_rate[year]["School Early Elderly Count"].get(ward, 0)
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
                    line=dict(color=color),
                )
            )
            if len(ward_select) <= 2:
                title, ytitle = elderly_graphview(
                    fig,
                    years,
                    elderly_rates,
                    early_elderly_rates,
                    ward,
                    opt,
                    1,
                    color,
                    rev_color,
                    offset,
                    width,
                    base,
                )
            elif len(ward_select) > 2:
                title, ytitle = elderly_graphview(
                    fig,
                    years,
                    elderly_rates,
                    early_elderly_rates,
                    ward,
                    opt,
                    2,
                    color,
                    rev_color,
                    offset,
                    width,
                    base,
                )
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
        barmode="stack",
    )

    return fig


@callback(
    [
        Output("primary-care-modal", "is_open"),
        Output("primary-care-modal-header", "children"),
        Output("primary-care-modal-text", "children"),
    ],
    [
        Input("primary-care-download-button", "n_clicks"),
        Input("primary-care-cancel-button", "n_clicks"),
        Input("primary-care-download-confirm-button", "n_clicks"),
    ],
    [
        State("primary-care-modal", "is_open"),
        State("target_select", "value"),
        State("ward_select", "value"),
        State("primary-care-file-name-input", "value"),
        State("primary-care-zoom-range-store", "children"),
        State("overall_compare", "value"),
    ],
)
def toggle_modal(
    n_open,
    n_cancel,
    n_download,
    is_open,
    distinction,
    areas,
    file_name,
    zoom_range,
    show_overall_primary_care,
):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    file_name = re.sub(r"[\s　]+", "", file_name) if file_name else ""
    if file_name is None or file_name == "":
        file_name = "primary_care.csv(※ファイル名未入力時)"
    else:
        file_name = f"{file_name}.csv"
    if not isinstance(areas, list):
        areas = [areas]
    if show_overall_primary_care == ["c1"]:
        areas.append("全体")
    areas_text = ", ".join(filter(None, areas)) if areas else "選択されていません。"
    data = [
        {"label": "全体", "value": "全体P"},
        {"label": "全体", "value": "全体C"},
        {"label": "行政区別", "value": "行政区別P"},
        {"label": "行政区別", "value": "行政区別C"},
        {"label": "小学校区別", "value": "小学校区別P"},
        {"label": "小学校区別", "value": "小学校区別C"},
    ]

    distinction_text = next(
        (item["label"] for item in data if item["value"] == distinction),
    )
    if distinction == "全体P" or distinction == "全体C":
        distinction_text = "行政区、小学校区も含めたすべての区"
        areas_text = "---"
    if zoom_range:
        start_year = math.ceil(zoom_range[0])
        end_year = math.floor(zoom_range[1])
        year_text = f"{start_year}年 - {end_year}年"
    else:
        year_text = "すべての年度"

    modal_body_text = [
        html.Div("ファイル名"),
        html.P(file_name),
        html.Div("区別種類"),
        html.P(distinction_text),
        html.Div(
            [
                html.Div("選択区"),
                html.P(areas_text),
            ]
        ),
        html.Div("選択年度"),
        html.P(year_text),
    ]

    if button_id == "primary-care-download-button":
        return True, "ファイルの出力", modal_body_text
    elif button_id in [
        "primary-care-cancel-button",
        "primary-care-download-confirm-button",
    ]:
        return False, "", modal_body_text
    return is_open, "", modal_body_text


@callback(
    Output("primary-care-zoom-range-store", "children"),
    [
        Input("certification_rate_graph", "relayoutData"),
        Input("target_select", "value"),
        Input("ward_select", "value"),
    ],
)
def update_zoom_range_store(relayoutData, distinction, areas):
    if not relayoutData:
        return dash.no_update
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "target_select" or button_id == "ward_select":
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
        if relayoutData["xaxis.range[0]"] <= 2000:
            relayoutData["xaxis.range[0]"] += 2001
            relayoutData["xaxis.range[1]"] += 2001
        print(relayoutData)
        return [relayoutData["xaxis.range[0]"], relayoutData["xaxis.range[1]"]]
    return dash.no_update


@callback(
    Output("download-primary-care", "data"),
    [Input("primary-care-download-confirm-button", "n_clicks")],
    [
        State("target_select", "value"),
        State("ward_select", "value"),
        State("primary-care-file-name-input", "value"),
        State("primary-care-zoom-range-store", "children"),
        State("overall_compare", "value"),
    ],
    prevent_initial_call=True,
)
def download_file(
    n_clicks,
    target_select,
    ward_select,
    file_name,
    zoom_range,
    show_overall_primary_care,
):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "primary-care-download-confirm-button":
        filepath = "/usr/src/data/save/20240221primary_care.csv"
        df = pd.read_csv(filepath)
        df_filtered = filter_df_by_target_select(
            df, target_select, show_overall_primary_care
        )
        if not isinstance(ward_select, list):
            ward_select = [ward_select]
        if ward_select and (target_select != "全体P" and target_select != "全体C"):
            if show_overall_primary_care == ["c1"]:
                ward_select.append("全体")
            df_filtered = df_filtered[df_filtered["区名"].isin(ward_select)]
        if zoom_range:
            df_filtered = df_filtered[
                (df_filtered["年度"] >= float(zoom_range[0]))
                & (df_filtered["年度"] <= float(zoom_range[1]))
            ]
        if file_name is None or file_name == "":
            file_name = "primary_care"
        df_filtered = df_filtered.to_csv(index=False)
        b64 = base64.b64encode(df_filtered.encode("CP932")).decode("CP932")
        return dict(content=b64, filename=f"{file_name}.csv", base64=True)


def filter_df_by_target_select(df, target_select, show_overall_primary_care):
    if target_select == "全体P" or target_select == "全体C":
        filter_condition = ["全体", "行政区", "小学校区"]
    elif target_select == "行政区別P" or target_select == "行政区別C":
        filter_condition = ["行政区"]
    elif target_select == "小学校区別P" or target_select == "小学校区別C":
        filter_condition = ["小学校区"]
    if show_overall_primary_care == ["c1"]:
        filter_condition.append("全体")
    filtered_df = df[df["区別種類"].isin(filter_condition)]
    return filtered_df
