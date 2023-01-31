import dash
from dash import callback_context as ctx
from dash import (
    Output,
    Input,
    State,
    html,
    dcc,
    dash_table,
    page_container,
    page_registry,
    register_page,
)
from dash.exceptions import PreventUpdate

# from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc, dash_table, ServersideOutput, ServersideOutputTransform, page_container, page_registry, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


META_TAGS = [
    {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5",
    },
    {
        "name": "author",
        "content": "Collective Thinking"
    },
    {
        "name": "description",
        "content": "Use our tool to look up the salaries of University of California employees. You can visualize how UC employee wages compare to one another and change from year to year.",
    },
    {
        "name": "title",
        "content": "UC My Wages - Visualize Salaries of University of California Employees",
    },
]

app = dash.Dash(
    __name__,
    external_stylesheets = 
    [
        dbc.themes.FLATLY, 
        dbc.icons.BOOTSTRAP, 
    ],
    assets_folder="assets",
    use_pages=True,
    meta_tags=META_TAGS,
)
server = app.server

app.title = "UC My Wages - Visualize Salaries of University of California Employees"
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Bitter:ital,wght@0,200;0,300;0,500;0,700;1,700&family=Roboto:wght@400;500;700&display=swap');        </style>
        {%metas%}
        <title>UC My Wages</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script data-goatcounter="https://goatcounter-ekmk.onrender.com/count"
                async src="//goatcounter-ekmk.onrender.com/count.js"></script>
    </body>
</html>
"""

navbar = dbc.Navbar(
    [
        dbc.Col(
            html.A(
                dbc.NavbarBrand("UC My Wages", style={"font-weight": "400", "font-family": "Bitter"}),
                href="/",
                style={"textDecoration": "none"},
            ),
            width="auto",
            style={"padding-left": "1rem", "margin-right": "auto"},
        ),
        dbc.Col(
            [
            dbc.Nav(
                [
                    dbc.NavItem(
                        html.A(
                            "Dashboard",
                            href="/#dashboard",
                            className="page-link"
                        ),
                    ),
                    dbc.NavItem(
                        html.A(
                            "Data Viz",
                            href="/dataviz",
                            className="page-link",
                        )
                    ),
                ],
                style={"flex-direction": "row"},
                pills=True,
            ),],
            width="auto",
            style={"margin-left": "auto", "padding-right": "1rem"},
        ),
    ],
    class_name="mx-0",
    color="#1d4558",
    dark=True,
    sticky="top",
    className="navbar",
    style={"padding-bottom": "0", "padding-top": "0", "z-index": "4"},
)

app.layout = html.Div(
    [
        navbar,
        html.Div(
            [
                page_container,
            ],
        ),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.P(
                                "Follow us!",
                                style={
                                    "color": "white",
                                    "margin-bottom": "0",
                                    "font-size": "1.2rem",
                                },
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.A(
                                html.I(
                                    className="bi bi-twitter",
                                    style={"color": "white", "font-size": "1.5rem"},
                                ),
                                href="https://twitter.com/collthinking420",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.A(
                                html.I(
                                    className="bi bi-reddit",
                                    style={"color": "white", "font-size": "1.5rem"},
                                ),
                                href="https://www.reddit.com/user/collective_thinking/",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.A(
                                "#UCMyWages",
                                href="https://twitter.com/search?q=UCMyWages&src=typeahead_click&f=top",
                                style={
                                    "text-decoration": "none",
                                    "font-size": "1.2rem",
                                    "color": "#84E0E5",
                                },
                            ),
                            width="auto",
                            style={"margin-left": "auto", "padding-right": ".25rem"},
                        ),
                    ],
                    class_name="gx-2",
                    align="center",
                ),
            ],
            className="footer-div",
        ),
        # dbc.Modal(
        #     children=[
        #         dbc.ModalHeader(dbc.ModalTitle("Welcome to UC My Wages!")),
        #         dbc.ModalBody(
        #             children=[
        #                 dcc.Markdown(
        #                     "In line with the [University of California's commitment to transparency and public accountability](https://ucannualwage.ucop.edu/wage/), this project aims to help the public search for and visualize the UC's data on employee compensation. Use our **Dashboard** to look up the annual salary of any UC employee over the last 10 years."
        #                 ),
        #                 dcc.Markdown(
        #                     "We are also actively updating our **Data Viz** page, which includes data visualizations that provide some context to the bargaining info between the UC and its grad worker unions."
        #                 ),
        #             ]
        #         ),
        #         dbc.ModalFooter(dbc.Button("Close", id="close-modal-button")),
        #     ],
        #     is_open=True,
        #     id="landing-modal",
        #     centered=True,
        # ),
    ],
    className="app-div",
)

# # --------------- callback - close modal -------
# # triggered by pressing the close button
# @app.callback(
#     Output("landing-modal", "is_open"),
#     Input("close-modal-button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def close_modal(n_clicks):
#     return False


# run script
if __name__ == "__main__":
    app.run_server(debug=True)
