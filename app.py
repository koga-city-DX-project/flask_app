import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash import dcc, html
from dash.dependencies import Input, Output

from pages import home, primary_care, select_care, tax

page_layouts = {
    "/": select_care.layout,
    "/tax": tax.layout,
    "/primary_care": primary_care.layout,
    "/home": home.layout,
}
external_stylesheets = ["bootstrap.min.css"]
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
)
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
                dbc.Col(content, id="content", style={"padding": "0"}),
            ],
            justify="start",
        )
    ],
    fluid=True,
)


@app.callback([Output("page-content", "children")], [Input("url", "pathname")])
def display_page(pathname):
    return_content = page_layouts.get(pathname, "404 not found")
    return [return_content]


if __name__ == "__main__":
    app.run_server(port=5000, debug=True, host="0.0.0.0", use_reloader=True)
