import math
import os
import re
from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, callback, dcc, html, no_update

data_directory = "/usr/src/data/save/"
file_pattern = re.compile(r"認定状態・総人口20(\d{2}).csv")

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


def update_code_maps(df, district_code_map, school_zone_code_map):
    """
    新たに見つかった行政区および小学校区に対してコードをマッピングし、
    district_code_mapとschool_zone_code_mapを更新する関数。

    Parameters:
    - df: データを含むPandas DataFrame。
    - district_code_map: 既存の行政区とコードのマッピングを含む辞書。
    - school_zone_code_map: 既存の小学校区とコードのマッピングを含む辞書。

    Returns:
    - 更新されたdistrict_code_mapとschool_zone_code_map。
    """
    # 行政区に対する処理
    for district in df["行政区"].dropna().unique():
        if district not in district_code_map:
            code = df[df["行政区"] == district].iloc[0]["自治会コード"]
            district_code_map[district] = (
                int(str(code)[:1]) if len(str(code)) == 3 else int(str(code)[:2])
            )

    # 小学校区に対する処理
    for school_zone in df["小学校区コード名"].dropna().unique():
        if school_zone not in school_zone_code_map:
            code = df.loc[df["小学校区コード名"] == school_zone, "小学校区コード"].iloc[0]
            school_zone_code_map[school_zone] = code

    return district_code_map, school_zone_code_map


aging_data = {}
district_code_map: Dict[str, int] = {}
school_zone_code_map: Dict[str, int] = {}
district_names: List[str] = []
school_zone_names: List[str] = []


def create_aging_data():
    """
    高齢化率の年次推移を計算する関数。
    """
    global aging_data, district_code_map, school_zone_code_map, district_names, school_zone_names
    for file_name in os.listdir(data_directory):
        match = file_pattern.match(file_name)
        if match:
            year = int("20" + match.group(1))
            file_path = os.path.join(data_directory, file_name)
            df = pd.read_csv(file_path, encoding="utf-8", dtype=column_types)
            total_population = len(df)
            df["年齢"] = year - df["生年月日_year"]
            elderly_data = df[df["年齢"] >= 65].copy()
            total_elderly_population = len(elderly_data)
            elderly_data.loc[:, "行政区"] = elderly_data["自治会コード名"].str.extract(r"^(.*区)")

            df.loc[:, "行政区"] = df["自治会コード名"].str.extract(r"^(.*区)")
            district_code_map, school_zone_code_map = update_code_maps(
                df, district_code_map, school_zone_code_map
            )

            district_elderly_counts = elderly_data.groupby("行政区").size()
            district_population_counts = df.groupby("行政区").size()

            school_zone_elderly_counts = elderly_data.groupby("小学校区コード名").size()
            school_zone_population_counts = df.groupby("小学校区コード名").size()

            district_elderly_counts = district_elderly_counts.reindex(
                district_population_counts.index, fill_value=0
            )
            school_zone_elderly_counts = school_zone_elderly_counts.reindex(
                school_zone_population_counts.index, fill_value=0
            )

            aging_rate_district = district_elderly_counts / district_population_counts
            aging_rate_school_zone = (
                school_zone_elderly_counts / school_zone_population_counts
            )
            aging_data[year] = {
                "TotalPopulation": total_population,
                "TotalElderlyPopulation": total_elderly_population,
                "AgingRateDistrict": aging_rate_district.to_dict(),
                "AgingRateSchoolZone": aging_rate_school_zone.to_dict(),
                "ElderlyCountsDistrict": district_elderly_counts.to_dict(),
                "ElderlyCountsSchoolzone": school_zone_elderly_counts.to_dict(),
            }

    for year_data in aging_data.values():
        district_names.extend(year_data["AgingRateDistrict"].keys())
        school_zone_names.extend(year_data["AgingRateSchoolZone"].keys())

    district_names = sorted(list(set(district_names)))
    school_zone_names = sorted(list(set(school_zone_names)))
    for year, data in aging_data.items():
        school_zone_rates = list(data["AgingRateSchoolZone"].values())
        average_rate_school_zone = (
            sum(school_zone_rates) / len(school_zone_rates) if school_zone_rates else 0
        )
        aging_data[year]["AverageAgingRateSchoolZone"] = average_rate_school_zone


def create_data_to_export():
    """
    出力するデータを作成する関数。
    """
    data_to_export = []
    for year, data in aging_data.items():
        for district, rate in data["AgingRateDistrict"].items():
            district_code = district_code_map.get(district, 0)
            data_to_export.append(
                [
                    year,
                    "行政区",
                    district,
                    rate,
                    district_code,
                ]
            )
        for school_zone, rate in data["AgingRateSchoolZone"].items():
            school_zone_code = school_zone_code_map.get(school_zone, 0)
            data_to_export.append(
                [
                    year,
                    "小学校区",
                    school_zone,
                    rate,
                    school_zone_code,
                ]
            )

    df_export = pd.DataFrame(
        data_to_export, columns=["年度", "区別種類", "区名", "高齢化率", "コード"]
    )

    df_export.sort_values(
        by=["年度", "区別種類", "コード"], ascending=[False, True, True], inplace=True
    )

    df_export = df_export.drop("コード", axis=1)
    filepath = "/usr/src/data/save/20240124aging_rate.csv"
    df_export.to_csv(filepath, index=False)


contents = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [html.H6("高齢化率(行政区・小学校区別)")],
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
                    [
                        dcc.Graph(
                            id="aging-rate-graph",
                            style={"height": "80vh"},
                        ),
                        html.Pre(id="relayout-data"),
                        html.Div(
                            id="aging-zoom-range-store", style={"display": "none"}
                        ),
                    ]
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
                        html.P("区別種類の選択", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="select-distinction-dropdown",
                            options=[
                                {"label": "行政区別", "value": "district"},
                                {"label": "小学校区別", "value": "schoolzone"},
                            ],
                            value="district",
                            className="setting_dropdown",
                            placeholder="種類を選択してください",
                        ),
                        html.P("表示区の絞り込み", className="font-weight-bold option_P"),
                        dcc.Dropdown(
                            id="display-area-dropdown",
                            options=[],
                            value=[],
                            multi=True,
                            className="setting_dropdown",
                            placeholder="すべての区を表示",
                        ),
                        html.Br(),
                        dbc.Input(
                            id="file-name-input",
                            placeholder="ファイル名を入力",
                            type="text",
                            className="setting_button",
                        ),
                        dbc.Button(
                            id="aging-download-button",
                            children="ファイルの出力",
                            className="text-white setting_button d-flex justify-content-center",
                            external_link="true",
                            color="secondary",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(id="aging-modal-header"),
                                dbc.ModalBody(
                                    [
                                        html.Div(id="aging-modal-text"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "ダウンロード",
                                                    id="download-confirm-button",
                                                    color="secondary",
                                                    className="me-2 bg-primary",
                                                ),
                                                dbc.Button(
                                                    "戻る",
                                                    id="cancel-button",
                                                    color="secondary",
                                                ),
                                            ],
                                            className="d-flex justify-content-center",
                                        ),
                                    ]
                                ),
                            ],
                            id="aging-modal",
                            is_open=False,
                        ),
                        dcc.Download(id="download-aging-rate"),
                    ],
                    className="setting d-grid",
                ),
            ],
            style={"height": "25vh", "marginLeft": "1px"},
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

create_aging_data()  # グラフ表示用のデータを作成
create_data_to_export()  # 出力用のデータを作成


@callback(
    Output("aging-rate-graph", "figure"),
    [
        Input("select-distinction-dropdown", "value"),
        Input("display-area-dropdown", "value"),
    ],
)
def update_graph(selected_distinction, selected_areas):
    fig = go.Figure(
        layout=dict(
            title=dict(text="高齢化率の年次推移", font=dict(size=24)),
            xaxis=dict(title="年度", title_font=dict(size=20)),
            yaxis=dict(title="高齢化率(%)", title_font=dict(size=20)),
            yaxis2=dict(
                title="高齢者総数",
                title_font=dict(size=20),
                overlaying="y",
                side="right",
                tickformat=",",
            ),
            hovermode="closest",
            showlegend=True,
        )
    )
    years = sorted(aging_data.keys())

    if selected_distinction is None:
        selected_distinction = "district"
        code_map = district_code_map
    if selected_distinction == "district":
        code_map = district_code_map
        areas = district_names if not selected_areas else selected_areas
        aging_rate_key = "AgingRateDistrict"
    elif selected_distinction == "schoolzone":
        code_map = school_zone_code_map
        areas = school_zone_names if not selected_areas else selected_areas
        aging_rate_key = "AgingRateSchoolZone"

    areas = sorted(areas, key=lambda area: code_map.get(area, float("inf")))
    for area in areas:
        if area != "average":
            aging_rates = [
                100 * aging_data[year][aging_rate_key].get(area, 0) for year in years
            ]
            if len(selected_areas) == 1:
                elderly_counts = [
                    aging_data[year][
                        f"ElderlyCounts{selected_distinction.capitalize()}"
                    ].get(area, 0)
                    for year in years
                ]
                fig.add_trace(
                    go.Bar(
                        x=years,
                        y=elderly_counts,
                        name=f"{area} 高齢者総数",
                        yaxis="y2",
                        marker=dict(opacity=0.6),
                    )
                )
            fig.add_trace(
                go.Scatter(x=years, y=aging_rates, mode="lines+markers", name=area)
            )

    if "average" in selected_areas or not selected_areas:
        average_aging_rates_school_zone_list = [
            100 * aging_data[year]["AverageAgingRateSchoolZone"] for year in years
        ]
        fig.add_trace(
            go.Scatter(
                x=years,
                y=average_aging_rates_school_zone_list,
                mode="lines+markers",
                name="全体の平均",
            )
        )
        if len(selected_areas) == 1:
            elderly_counts = [
                aging_data[year]["TotalElderlyPopulation"] for year in years
            ]
            fig.add_trace(
                go.Bar(
                    x=years,
                    y=elderly_counts,
                    name="高齢者総数(人)",
                    yaxis="y2",
                    marker=dict(opacity=0.6),
                )
            )

    return fig


@callback(
    Output("display-area-dropdown", "options"),
    [Input("select-distinction-dropdown", "value")],
)
def update_display_area_options(selected_distinction):
    options = []
    if selected_distinction == "district":
        sorted_districts = sorted(
            district_code_map.keys(), key=lambda x: district_code_map[x]
        )
        options = [
            {"label": district, "value": district} for district in sorted_districts
        ]

    elif selected_distinction == "schoolzone":
        sorted_school_zones = sorted(
            school_zone_code_map.keys(), key=lambda x: school_zone_code_map[x]
        )
        options = [
            {"label": school_zone, "value": school_zone}
            for school_zone in sorted_school_zones
        ]

    options.append({"label": "全体の平均", "value": "average"})

    return options


@callback(
    [
        Output("aging-modal", "is_open"),
        Output("aging-modal-header", "children"),
        Output("aging-modal-text", "children"),
    ],
    [
        Input("aging-download-button", "n_clicks"),
        Input("cancel-button", "n_clicks"),
        Input("download-confirm-button", "n_clicks"),
    ],
    [
        State("aging-modal", "is_open"),
        State("select-distinction-dropdown", "value"),
        State("display-area-dropdown", "value"),
        State("file-name-input", "value"),
        State("aging-zoom-range-store", "children"),
    ],
)
def toggle_modal(
    n_open, n_cancel, n_download, is_open, distinction, areas, file_name, zoom_range
):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    distinction_text = (
        "行政区別"
        if distinction == "district"
        else "小学校区別"
        if distinction == "schoolzone"
        else "未選択(※自動的に行政区別が選択されます)"
    )
    file_name = re.sub(r"[\s　]+", "", file_name) if file_name else ""
    if file_name is None or file_name == "":
        file_name = "aging_rate.csv(※ファイル名未入力時)"
    else:
        file_name = f"{file_name}.csv"
    areas_text = ", ".join(areas) if areas else "すべての区"
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

    if button_id == "aging-download-button":
        return True, "ファイルの出力", modal_body_text
    elif button_id in ["cancel-button", "download-confirm-button"]:
        return False, "", modal_body_text
    return is_open, "", modal_body_text


@callback(
    Output("download-aging-rate", "data"),
    [Input("download-confirm-button", "n_clicks")],
    [
        State("select-distinction-dropdown", "value"),
        State("display-area-dropdown", "value"),
        State("file-name-input", "value"),
        State("aging-zoom-range-store", "children"),
    ],
    prevent_initial_call=True,
)
def download_file(n_clicks, distinction, areas, file_name, zoom_range):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "download-confirm-button":
        filepath = "/usr/src/data/save/20240124aging_rate.csv"
        df = pd.read_csv(filepath)
        df_filtered = filter_df_by_distinction(df, distinction)
        if areas:
            df_filtered = df_filtered[df_filtered["区名"].isin(areas)]
        if zoom_range:
            df_filtered = df_filtered[
                (df_filtered["年度"] >= float(zoom_range[0]))
                & (df_filtered["年度"] <= float(zoom_range[1]))
            ]
        if file_name is None or file_name == "":
            file_name = "aging_rate"
        return dcc.send_data_frame(df_filtered.to_csv, f"{file_name}.csv", index=False)


@callback(
    Output("aging-zoom-range-store", "children"),
    [
        Input("aging-rate-graph", "relayoutData"),
        Input("select-distinction-dropdown", "value"),
        Input("display-area-dropdown", "value"),
    ],
)
def update_zoom_range_store(relayoutData, distinction, areas):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # ドロップダウンメニューの選択が変更された時は初期化
    if (
        button_id == "select-distinction-dropdown"
        or button_id == "display-area-dropdown"
    ):
        return None
    # グラフ内でダブルクリックされた時は初期化
    if "xaxis.autorange" in relayoutData or "yaxis.autorange" in relayoutData:
        return None
    # 縦方向のみのズーム操作の時は更新しない
    if ("yaxis.range[0]" in relayoutData or "yaxis.range[1]" in relayoutData) and (
        "xaxis.range[0]" not in relayoutData or "xaxis.range[1]" not in relayoutData
    ):
        return no_update
    # 縦方向のズーム操作が含まれる時は更新する
    if (
        relayoutData
        and "xaxis.range[0]" in relayoutData
        and "xaxis.range[1]" in relayoutData
    ):
        return [relayoutData["xaxis.range[0]"], relayoutData["xaxis.range[1]"]]
    return no_update


def filter_df_by_distinction(df, distinction):
    if distinction == "district" or distinction is None:
        filter_condition = "行政区"
    elif distinction == "schoolzone":
        filter_condition = "小学校区"
    else:
        raise ValueError("Invalid distinction value")

    filtered_df = df[df["区別種類"] == filter_condition]
    filtered_df = filtered_df.drop(columns=["区別種類"])
    return filtered_df
