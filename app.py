import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html
from dash.dependencies import Input, Output

from pages import (  # aging_rate,; care_level_rate,; population_distribution,
    home,
    primary_care,
    select_care,
    select_populations,
    select_tax,
)

page_layouts = {
    "/": select_care.layout,
    "/select_tax": select_tax.layout,
    "/primary_care": primary_care.layout,
    "/home": home.layout,
    # "/care_level_rate": care_level_rate.layout,
    "/select_populations": select_populations.layout,
    # "/aging_rate": aging_rate.layout,
    # "/population_distribution": population_distribution.layout,
}
external_stylesheets = ["bootstrap.min.css"]
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    update_title=None,
)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="assets/style.css" rel="stylesheet" />
    </head>
    <body>
        <div id="js-loader" class="loader"></div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.title = "テストページ"
passPair = {"User1": "AAA", "User2": "BBB"}
auth = dash_auth.BasicAuth(app, passPair)
du.configure_upload(app, r"/usr/src/data")


content = html.Div(id="page-content")

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="shared-selected-df", storage_type="session"),
                dbc.Col(
                    content, id="content", style={"padding": "0", "height": "100vh"}
                ),
            ],
            justify="center",
            align="center",
            style={"height": "100vh"},
        )
    ],
    fluid=True,
    style={"height": "100vh"},
)


@app.callback([Output("page-content", "children")], [Input("url", "pathname")])
def display_page(pathname):
    return_content = page_layouts.get(pathname, "404 not found")
    return [return_content]


if __name__ == "__main__":
    app.run_server(port=5000, debug=True, host="0.0.0.0", use_reloader=True)
