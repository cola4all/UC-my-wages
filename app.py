import dash
from dash import callback_context as ctx
from dash import  Output, Input, State, html, dcc, dash_table, page_container, page_registry, register_page
from dash.exceptions import PreventUpdate
#from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc, dash_table, ServersideOutput, ServersideOutputTransform, page_container, page_registry, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# app = DashProxy(__name__, transforms=[ServersideOutputTransform()], external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], assets_folder='assets', use_pages=True,
#         meta_tags=[{
#             'name': 'viewport',
#             'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'        
#         }]
# )   
# app = DashProxy(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], assets_folder='assets', use_pages=True)   
# register_page("another_home", layout=html.Div("We're home!"), path="/")


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], assets_folder='assets', use_pages=True,
        meta_tags=[{
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'        
        }]
)   
server = app.server

app.title = "UC My Wages"
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
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
'''

navbar = dbc.Navbar(
    [
        dbc.Col(
            html.A(
                dbc.NavbarBrand("UC My Wages", style={"font-size": "1.5rem"}),
                href="#",
                style={"textDecoration": "none"},
            ),
            width="auto",
            style={"padding-left": "1rem"},
        ),
        dbc.Col(
            dbc.Nav(
                [
                    dbc.NavLink("Dashboard", href="/dashboard", style={"padding": "0.5rem"}, className="page-link"),
                    html.Hr(style={"height":"1.8rem", "margin":"0", "padding":"0", "align-self":"center", "border":"0.05rem solid #E3F9FA", "opacity":"0.25"}),
                    dbc.NavLink("Data Viz", href="/", style={"padding": "0.5rem"}, className="page-link")
                ],
                #vertical=False     # this doesn't behave as expected; so overwrite flex-direction and padding instead
                style={"flex-direction": "row"},
                pills=True,
            ),
            width="auto",
            style={"margin-left": "auto", "padding-right": "1rem"}
        ),
    ],
    class_name="mx-0",
    color="#005581",
    dark=True,
    sticky='top',
    className = "navbar",
    style={"padding-bottom": "0.25rem", "padding-top": "0.25rem"}
)

app.layout = html.Div([navbar,
    html.Div([
    page_container,],
    className="body-div"),
    html.Div([dbc.Row(
        [
        dbc.Col(html.P("Follow us!", style={"color":"white", "margin-bottom":"0", "font-size":"1.2rem"}), width="auto"),
        dbc.Col(html.A(html.I(className="bi bi-twitter", style={"color":"white", "font-size":"1.5rem"}), href="https://twitter.com/collthinking420"), width="auto"),
        dbc.Col(html.A(html.I(className="bi bi-reddit", style={"color":"white", "font-size":"1.5rem"}),href="https://www.reddit.com/user/collective_thinking/"), width="auto"),
        dbc.Col(html.A("#UCMyWages", href="https://twitter.com/search?q=UCMyWages&src=typeahead_click&f=top", style={"text-decoration":"none", "font-size":"1.2rem", "color":"#84E0E5"}), width="auto", style={"margin-left":"auto", "padding-right":".25rem"})
        ],
        class_name = "gx-2",
        align="center"
    ),
    ],
    className="footer-div"
    ),
    dbc.Modal(
        children = [
            dbc.ModalHeader(dbc.ModalTitle("UC My Wages")),
            dbc.ModalBody(
                children = [
                    dcc.Markdown("Welcome!"),
                    dcc.Markdown("In line with the [University of California's commitment to transparency and public accountability](https://ucannualwage.ucop.edu/wage/), this project aims to help the public search for and visualize the UC's data on employee compensation."),
                    dcc.Markdown("This app is a pet project under active development, so please bear with me as I continue to make improvements.")
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal-button")
            ),
        ],
        is_open=True,
        id='landing-modal',
        centered=True)
    ],
    className="app-div",
)

#--------------- callback - close modal -------
# triggered by pressing the close button
@app.callback(
    Output("landing-modal", "is_open"),
    Input("close-modal-button", "n_clicks"),
    prevent_initial_call = True
)
def close_modal(n_clicks): 
    return False






# run script
if __name__ == '__main__':
     app.run_server(debug=True)