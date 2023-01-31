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
    callback,
)
from dash.exceptions import PreventUpdate

# from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc, dash_table, ServersideOutput, ServersideOutputTransform, page_container, page_registry, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os, pathlib
import time

register_page(__name__, path="/", title="UC My Wages", description="Use our tool to look up the salaries of University of California employees. You can visualize how UC employee wages compare to one another and change from year to year.")

# define paths
APP_PATH = os.path.split(str(pathlib.Path(__file__).parent.resolve()))[0]
JOB_DATA_PATH = os.path.join(APP_PATH, "assets", "salaries_by_job.parquet")
NAME_DATA_PATH = os.path.join(APP_PATH, "assets", "salaries_by_name.parquet")


# create schemas so that you don't need to remember the labels when coding
class DataSchema:
    NAME = "Employee Name"
    JOB = "Job Title"
    JOB_ABBREVIATED = "Abbreviated Job Title"
    TOTAL_PAY = "Total Pay"
    TOTAL_PAY_AND_BENEFITS = "Total Pay & Benefits"
    YEAR = "Year"
    PRIORPAY = "Prior Year Pay"
    ADJUSTMENT = "Adjustment"
    CUMADJUSTMENT = "Cumulative Adjustment"
    PROJECTEDPAY = "Projected Pay"


class ids:
    PROJECTED_WAGES_LINE_PLOT = "projected-wages-line-plot"
    REAL_WAGES_LINE_PLOT = "real-wages-line-plot"
    RATE_JOB_DROPDOWN = "rate-job-dropdown"
    RATE_NAME_DROPDOWN = "rate-name-dropdown"
    RATE_COLA_DROPDOWN = "rate-cola-dropdown"
    INITIAL_WAGE_DROPDOWN = "initial-wage-dropdown"
    INITIAL_WAGE_INPUT = "initial-wage-input"
    LOLLIPOP_CHART = "lollipop-chart"
    NAME_SEARCH_CONTAINER = "name-search-container"
    NAME_SEARCH_INPUT = "name-search-input"
    NAME_SEARCH_BUTTON = "name-search-button"
    NAME_SEARCH_RESULTS_CONTAINER = "name-search-results-container"
    NAME_SEARCH_RESULTS_TABLE = "name-search-results-table"
    NAME_ADD_CONTAINER = "name-add-container"
    NAME_ADDED_DROPDOWN = "name-added-dropdown"
    NAME_ADD_BUTTON = "name-add-button"
    NAME_CONTAINER = "name-container"
    YEAR_RANGE_CONTAINER = "year-range-container"
    YEAR_RANGE_SLIDER = "year-range-slider"
    INITIAL_WAGE_CONTAINER = "initial-wage-container"
    PROPOSAL_LOLLIPOP_PLOT = "proposal-lollipop-plot"


class colors:
    PLOT_BACKGROUND_COLOR = "#edeff1"
    END_MARKER_COLOR = "#355218"
    START_MARKER_COLOR = "#759356"
    LOLLIPOP_LINE_COLOR = "#7B7B7B"
    GRID_LINES_COLOR = "#C5CCCA"


t0 = time.time()
print("reading csv 1:")
# load data
df_jobs = pd.read_parquet(
    JOB_DATA_PATH, engine="fastparquet"
)  # need to create parquet file first
print(time.time() - t0)


t0 = time.time()
print("reading csv 2:")
df_names = pd.read_parquet(NAME_DATA_PATH, engine="fastparquet")
print(time.time() - t0)

print("size of df_names_filtered:")
print(df_names.info(memory_usage="deep"))

t0 = time.time()

cat_type_year = pd.api.types.CategoricalDtype(
    categories=[2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],
    ordered=True,
)
df_jobs["Year"] = df_jobs["Year"].astype(cat_type_year)
df_names["Year"] = df_names["Year"].astype(cat_type_year)

# t0 = time.time()
print("creating html components:")
# ------------- create html components --------------------
# better way to do this? this is faster than reading a df
unique_jobs = df_jobs["Employee Name"].unique().tolist()

job_container = html.Div(
    children=[
        html.P("Select a position to add to the plots:", id="job-label"),
        dcc.Dropdown(
            id=ids.RATE_JOB_DROPDOWN,
            options=unique_jobs,
            value=[
                "GSR (Step 5)",
                "Teaching Assistant",
                "Assistant Professor (II)",
                "Associate Professor (II)",
                "Professor (II)",
            ],
            multi=True,
        ),
    ]
)

# TODO: implement cola
# cola_container = html.Div(
#     className='dropdown-container',
#     children = [
#         html.Label("Select COLA", id="cola-label"),
#         dcc.Dropdown(
#             id=ids.RATE_COLA_DROPDOWN,
#             options=["Santa Barbara", "Los Angeles", "San Francisco"],
#             value="Santa Barbara",
#             multi=False
#         )
#     ]
# )


OFFCANVAS_NAV_STYLE = {
    "position": "fixed",
    "top": "-3rem",
    "width": "100%",
    "background-color": "#48a8d7",
    "transition": "top 0.8s",
    "z-index": "3",
}

offcanvas_nav = dbc.Nav(
    [
        dbc.Button(
            [
                html.I(
                    className="bi bi-sliders",
                    style={
                        "color": "white",
                        "font-size": "1rem",
                        "margin-right": ".6rem",
                    },
                ),
                "Plot Controls",
            ],
            id="open-offcanvas",
            n_clicks=0,
            class_name="button",
        ),
    ],
    vertical=True,
    pills=True,
    style=OFFCANVAS_NAV_STYLE,
    class_name="fixed-top",
    id="filter-navbar",
)

compensation_type_container = dbc.Row(
    [
        dbc.Col(
            dbc.Label("Compensation Type:", style={"margin": "0"}),
            width="auto",
            id="compensation-type-label-container",
        ),
        dcc.Dropdown(
            options=[
                "Total Pay & Benefits",
                "Total Pay",
            ],
            value="Total Pay",
            multi=False,
            clearable=False,
            id="select-compensation-dropdown",
        ),
    ],
    style={
        "align-items": "stretch",
        "justify-content": "flex-start",
        "margin": "0",
    },
)

year_range_slider = dcc.RangeSlider(
    min=2011,
    max=2021,
    step=1,
    value=[2011, 2021],
    marks={
        2011: "2011",
        2012: "2012",
        2013: "2013",
        2014: "2014",
        2015: "2015",
        2016: "2016",
        2017: "2017",
        2018: "2018",
        2019: "2019",
        2020: "2020",
        2021: "2021",
    },
    id=ids.YEAR_RANGE_SLIDER,
)

GRAY_BACKGROUND = "#ecf0f1"
GRAY_OUTLINE = "#cccccc"
year_range_container = dbc.Row(
    [
        dbc.Col(
            dbc.Label("Year Range:", style={"margin": "0"}),
            width="auto",
            id="year-range-label-container",
        ),
        dbc.Col(
            year_range_slider,
            id="year-range-slider-container",
        ),
    ],
    style={
        "align-items": "stretch",
        "justify-content": "flex-start",
        "margin": "0",
    },
)

add_positions_container = html.Div(
    [
        html.Div(
            html.Span("Add Positions:"),
            id="add-positions-label-container",
        ),
        dcc.Dropdown(
            options=unique_jobs,
            value=[
                "GSR (Step 5)",
                "Teaching Assistant",
                "Assistant Professor (II)",
                "Associate Professor (II)",
                "Professor (II)",
            ],
            multi=True,
            placeholder="select or search...",
            id=ids.RATE_JOB_DROPDOWN,
        ),
    ],
    style={"display": "flex", "flex-wrap": "wrap"},
)

name_search_container = html.Div(
    [
        dbc.Input(
            id=ids.NAME_SEARCH_INPUT,
            placeholder="enter an employee name...",
            debounce=True,
        ),
        dbc.Button("Search", id="name-search-button", className="button"),
    ],
    style={"display": "flex", "flex-wrap": "nowrap"},
)

name_search_results_container = html.Div(
    id=ids.NAME_SEARCH_RESULTS_CONTAINER,
    children=[
        dash_table.DataTable(id=ids.NAME_SEARCH_RESULTS_TABLE),
    ],
)

name_add_container = html.Div(
    [
        dbc.Button("Add Selected Name", id=ids.NAME_ADD_BUTTON, className="button"),
        dcc.Dropdown(
            id=ids.NAME_ADDED_DROPDOWN,
            value=[],
            options=[],
            multi=True,
            placeholder="add selected employee to plots...",
        ),
    ],
    id=ids.NAME_ADD_CONTAINER,
    style={
        "display": "flex",
        "flex-wrap": "wrap",
        "align-items": "stretch",
    },
)

name_random_container = html.Div(
    [
        html.Div(
            html.Span("Can't think of a name?"),
            id="random-name-label-container",
        ),
        dbc.Button("Add Random Name", id="random-name-button", className="button"),
    ],
    id="name-random-container",
    style={
        "display": "flex",
        "flex-wrap": "nowrap",
        "align-items": "stretch",
    },
)

add_employees_container = html.Div(
    [
        html.Div(
            html.Span("Add Employees"),
            id="add-employees-label-container",
        ),
        html.Div(
            [
                name_search_container,
                html.P(),
                name_search_results_container,
                html.P(),
                name_add_container,
                html.P(),
                #name_random_container,
            ],
            id="add-employees-body",
            style={
                "padding-left": "1rem",
                "padding-right": "1rem",
            },
        ),
    ],
    style={"display": "flex", "flex-wrap": "wrap"},
)

OFFCANVAS_STYLE = {
    "top": "5rem",
    "width": "100%",
    "height": "75%",
    "z-index": "2",
}

offcanvas = dbc.Offcanvas(
    [
        compensation_type_container,
        html.H1(),
        year_range_container,
        html.H1(),
        add_positions_container,
        html.H1(),
        add_employees_container,
    ],
    id="offcanvas",
    title="Plot Options",
    is_open=False,
    scrollable=True,
    placement="top",
    backdrop=True,  # need to create a transparent backdrop to be able to close by clicking offscreen
    backdrop_class_name="offcanvas-backdrop",
    style=OFFCANVAS_STYLE,
)

# hero section
hero_div = html.Div(
    [
        html.Div(
            html.H1(
                [
                    " Bringing ",
                    html.Br(className="hero-header-breaks"),
                    html.Span("Pay Transparency ", style={"font-weight": "700", "color": "#82dee3"}),
                    html.Br(),
                    "to the ",
                    html.Br(className="hero-header-breaks"),
                    html.Span("University of California", style={"font-weight": "700"}),
                ],
            ),
            id="hero-header",
        ),
        html.Div(
            html.P(
                [
                    " The UC discloses employee wage data as part of its commitment to ",
                    html.Span("public accountability", className = "emphasis-text"),
                    ". But without ",
                    html.Span("context", className = "emphasis-text"),
                    ", this information is just raw numbers. ",
                    "Our ",
                    html.Span("Wages Dashboard ", className = "emphasis-text"),
                    "puts the data into perspective and helps deliver ",
                    html.Span("real transparency ", className = "emphasis-text"),
                    "by visualizing how UC employee wages ",
                    html.Span("compare to one another "),
                    "and ",
                    html.Span("change over time"),
                    ".",
                ],
                id="hero-text",
            ),
            id="hero-text-div",
        ),
        html.Div(
            [
                html.A("Explore Wages Dashboard", href="#dashboard", className="hero-button", id="hero-primary-button"),
                html.A("View Data Viz Collection", href="/dataviz", className="hero-button", id="hero-secondary-button")
            ],
            id="hero-buttons-div"
        ),
    ],
    id="hero-div",
    style={
        "display": "flex",
        "flex-wrap": "wrap",
        "justify-content": "center",
        "color": "white",
    },
)

# Knowing the wages of your bosses and peers is typically a taboo subject, and keeping this information hidden from employees is a way of reinforcing the power dynamics. Without this transparency, bosses can give preferential raises to themselves or their favorite employees, and not have to worry about accountability. The wages dashboard includes data from all UC employees - including facilities and hospitality workers, nurses, clerical workers, doctors, etc. some of these groups are unionized and when their negotiations with UC comes around, the tool can be a handy way to look at their wages in context. Also importantly, if UC managers know that their raises and their employee raises are being tracked, they will be more conscious about providing fair compensation throughout the system.

# create layout
layout = html.Div(
    [
        offcanvas_nav,
        offcanvas,
        hero_div,
        html.Div(
            children=[
                html.Div(
                    id="content-div",
                    children=[
                        # data stores
                        dcc.Store(id="filtered-names-data"),
                        dcc.Store(id="filtered-jobs-data"),
                        dcc.Store(id="filtered-combined-data"),
                        dcc.Store(id="jobs-data"),
                        dcc.Store(id="names-data"),
                        dcc.Store(id="table-data-records-list"),
                        dcc.Store(id="traces-in-real-wages"),
                        dcc.Store(id="traces-in-projected-wages"),
                        dcc.Store(id="compensation-type-store"),
                        dcc.Interval(
                            id="page-load-interval",
                            n_intervals=0,
                            max_intervals=0,
                            interval=1,
                        ),  # max_intervals = 0 ensures callback only runs once at startup
                        html.A(id="dashboard"),
                        html.H4(
                            "How does your compensation stack up against other UC employees?"
                        ),
                        dcc.Markdown(
                            "Open the plot controls and search for UC employees by name to add them to the plots. You can also search for certain positions to plot their aggregated wage data. Hover or click on a data point to compare across all employees for that year."
                        ),
                        html.Div(
                            [
                                html.P(),
                                dbc.Row(
                                    [
                                        dbc.Col(dbc.Label("linear"), className="pe-2"),
                                        dbc.Col(
                                            dbc.Switch(
                                                value=False,
                                                id="real-wages-scale-switch",
                                            ),
                                            className="p-0",
                                        ),
                                        dbc.Col(dbc.Label("log"), className="p-0"),
                                    ],
                                    className="d-inline-flex g-0 align-items-start",
                                ),
                            ]
                        ),
                        dcc.Graph(
                            id=ids.REAL_WAGES_LINE_PLOT,
                            config={"displayModeBar": False},
                            figure={"layout": {"autosize": True, "fillframe": True}},
                        ),
                        html.Hr(),
                        html.H4(
                            "Ever wonder what your compensation might be if it grew at the same rate as your peers, employees, or bosses?"
                        ),
                        dcc.Markdown(
                            "This plot projects how your specified starting compensation would change if you received the same year-to-year percentage-based raises as other employees. *Simply set your starting compensation below. You may also need to adjust the year range slider (this rescales the x-axis) to fit the range of years for which the employee has data.*"
                        ),
                        dbc.Accordion(
                            children=[
                                dbc.AccordionItem(
                                    children=[
                                        html.P(
                                            "Set a starting compensation by selecting a job or entering a custom amount:"
                                        ),
                                        dcc.Dropdown(
                                            id=ids.INITIAL_WAGE_DROPDOWN,
                                            options=unique_jobs,
                                            value="GSR (Step 5)",
                                            placeholder="Set an starting compensation based on job or enter custom value on the right",
                                            multi=False,
                                            clearable=False,
                                        ),
                                        dcc.Input(
                                            id=ids.INITIAL_WAGE_INPUT,
                                            value=22900,  # old code: value = df_jobs.loc[(df_jobs[DataSchema.NAME]=="GSR (Step 1)") & (df_jobs[DataSchema.YEAR]==2011), DataSchema.PAY].iloc[0],
                                            type="number",
                                            placeholder="",
                                            debounce=True,
                                        ),
                                    ],
                                    title="Starting Compensation: $" + str(16698),
                                    id="initial-wage-accordion-item",
                                ),
                            ],
                            always_open=True,
                            active_item=[
                                "item-0",
                                "item-1",
                            ],  # this needs to be string id (not assigned id, which starts at 0)
                            id="bottom-accordion",
                        ),
                        dcc.Graph(
                            id=ids.PROJECTED_WAGES_LINE_PLOT,
                            config={"displayModeBar": False},
                        ),
                        html.Hr(),
                        html.H4(
                            "How do your raises compare in terms of the absolute dollar amount?"
                        ),
                        dcc.Markdown(
                            "We tend to talk about year-to-year raises in terms of percentages, but this obscures the fact that our **absolute wage growth** depends on this percentage **as well as our prior year's salary.** Tying our raises to our prior year's salary is great for high-income earners, but not so much for low-income workers. **This system locks lower-paid positions out of real wage growth, puts workers at the mercy of unpredictable rises in cost of living, and exacerabates income disparities between higher-paid executives and lower-paid workers.**"
                        ),
                        dcc.Markdown(
                            "See how this disparity plays out in the UC system by comparing higher-paid employees to lower-paid employees in the following plot. The length of each line conveys a sense of the employee's raise over the provided year range. The further to the right, the more the employee earns."
                        ),
                        dcc.Markdown(
                            "*If an employee that you added is missing from the plot, adjust the year range slider (above) to match the years for which that employee has data.*"
                        ),
                        html.H5("Years: 2011-2021", id="lollipop-chart-title"),
                        dcc.Graph(
                            id=ids.LOLLIPOP_CHART, config={"displayModeBar": False}
                        ),
                        html.Hr(),
                        dbc.Accordion(
                            children=[
                                dbc.AccordionItem(
                                    children=[
                                        dcc.Markdown(
                                            "Data for UC employee wages are publicly available and retrieved from [Transparent California](https://transparentcalifornia.com/salaries/2021/university-of-california/)."
                                        ),
                                        dcc.Markdown(
                                            "Graduate student research (GSR) pay scales from 2011-2021 are retrieved from [here](https://grad.ucsd.edu/financial/employment/student-pay-rates.html)."
                                        ),
                                        dcc.Markdown(
                                            "Professor pay scales from 2011-2021 are retrieved from [here](https://ap.uci.edu/compensation/salary-scales/)."
                                        ),
                                    ],
                                    title="Data Sources",
                                ),
                                dbc.AccordionItem(
                                    children=[
                                        dcc.Markdown(
                                            "**This project is an active work in progress.** We are making this tool available to the public in its current state because of its relevance to the ongoing labor dispute between the UC and its 48,000 Academic Workers. It is our hope that this project helps the UC on its commitment to [Accountability and Transparency](https://ucannualwage.ucop.edu/wage/)."
                                        ),
                                        dcc.Markdown(
                                            "The following are some limitations and features on our to-do list:"
                                        ),
                                        dcc.Markdown(
                                            """
                                    * Currently, the app is unable to distinguish between employees who share the same name. The app currently aggregates all employees of the same name for a given year. A future release will be able to distinguish these employees.
                                    * Employees making under $30K were removed from the current database. These may be added back in in the future.
                                    * Improving the speed of generating new plots
                                    * Streamlining the UI and making it more mobile-friendly and responsive across all screen sizes
                                    * Creating a more robust pattern-matching for the employee name search
                                    * Adding reference lines like Cost of Living for different cities to the plots
                                    * Additional visualizations may be added in the future.
                                """
                                        ),
                                        dcc.Markdown(
                                            "Please [DM us on twitter](https://twitter.com/collthinking420) if you wish to report any bugs or feature requests."
                                        ),
                                    ],
                                    title="Limitations and Future Releases",
                                ),
                            ],
                            active_item=[],
                        ),
                    ],
                    # style=CONTENT_STYLE,
                )
            ],
            style={"display": "flex", "flex-direction": "column"},
            className="body-div",
            
        ),
    ]
)


print(time.time() - t0)

# --------------- callback - dropdown -------
# also - dsiable/enable refresh plot
@callback(
    Output("compensation-type-store", "data"),
    # Output("compensation-accordion-item", "title"),
    Input("select-compensation-dropdown", "value"),
    prevent_initial_call=False,  # want to load in background
)
def set_compensation(COMPENSATION_TYPE):

    if COMPENSATION_TYPE is None:
        COMPENSATION_TYPE = "Total Pay"  # sets default COMPENSATION_TYPE here

    COMPENSATION_TYPE = "".join(COMPENSATION_TYPE)  # coerce a list to string

    if COMPENSATION_TYPE is None:
        raise PreventUpdate

    # DataSchema.PAY = compensation_type      # bad: changing global variable interferes if two instances are run on one server

    # title = "Type of Compensation: " + COMPENSATION_TYPE

    return COMPENSATION_TYPE


# ------------- callback - save_datastore ----------------------
# triggered by landing modal changing
# @callback(
#     Output("jobs-data", "data"),
#     Output("names-data",'data'),
#     Output('select-compensation-dropdown', 'value'),
#     Input('page-load-interval', 'n_intervals'),
#     State('jobs-data', 'data'),
#     State('names-data', 'data'),
#     State('select-compensation-dropdown', 'value'),
#     prevent_initial_call = False)
# def save_datastore(n_intervals, jobs_data, names_data, COMPENSATION_TYPE):
#     if COMPENSATION_TYPE is None:
#         COMPENSATION_TYPE = 'Total Pay'     # sets default COMPENSATION_TYPE here

#     # names_data can be filtered by year? and earnings?
#     if (jobs_data is None) and (names_data is None):
#         return df_jobs, df_names, COMPENSATION_TYPE
#     else:
#         raise PreventUpdate

## callback - toggle off-canvas
@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


# # ------------- callback - search names in data frame ----------------
@callback(
    Output(ids.NAME_SEARCH_RESULTS_CONTAINER, "children"),
    Input(ids.NAME_SEARCH_BUTTON, "n_clicks"),
    Input(ids.NAME_SEARCH_INPUT, "n_submit"),
    State(ids.NAME_SEARCH_INPUT, "value"),
    prevent_initial_call=True,
)
def search_names(n_clicks, n_submit, search_name):
    print("entered search_names:")
    print(search_name)
    t0 = time.time()
    # handle if names is empty
    if (search_name is None) or (df_names is None):
        raise PreventUpdate
    # handle if no matches (maybe no need)

    # display unique matches
    df_names_match = df_names[
        df_names.loc[:, DataSchema.NAME].str.contains(
            search_name.casefold().strip(), regex=False
        )
    ]
    print("pandas str contains:")
    print(time.time() - t0)

    t0 = time.time()
    unique_names_match = list(set(df_names_match[DataSchema.NAME]))

    # early return if no matches/too many (todo: build robust table with navigation)
    if len(unique_names_match) > 200:
        too_many_matches = html.Div(
            children=[
                html.Label(
                    "Found too many matching results. Please enter a more specific name."
                ),
            ]
        )
        return too_many_matches
    elif len(unique_names_match) == 0:
        no_matches = html.Div(
            children=[
                html.Label(
                    "Could not find a matching result. Please search for another name.",
                    className = "search-alert-text"
                ),
            ],
            className = "search-alert-div"          
        )
        return no_matches

    # build df where each row is a unique employee w/ an employee name col and a years available col
    table_data_records_list = []
    for name in unique_names_match:
        years_available = (
            df_names_match[DataSchema.YEAR]
            .loc[df_names_match[DataSchema.NAME] == name]
            .to_list()
        )
        years_available_str = ", ".join([str(x) for x in years_available])
        table_data_records_list.append(
            {DataSchema.NAME: name, "Years Available": years_available_str}
        )
    print("rest of the script:")
    print(time.time() - t0)

    name_search_results_container_updated = html.Div(
        children=[
            html.Label("Select a name from search results:"),
            dash_table.DataTable(
                data=table_data_records_list,
                columns=[
                    {"name": DataSchema.NAME, "id": DataSchema.NAME},
                    {"name": "Years Available", "id": "Years Available"},
                ],
                active_cell={"column": 0, "row": 0},
                selected_cells=[{"column": 0, "row": 0}],
                id=ids.NAME_SEARCH_RESULTS_TABLE,
                style_data={"whiteSpace": "normal"},
            ),
        ]
    )
    return name_search_results_container_updated


# # ------------- callback - add selected name from table to the dropdown ----------------
@callback(
    Output(ids.NAME_ADDED_DROPDOWN, "value"),
    Output(ids.NAME_ADDED_DROPDOWN, "options"),
    Input(ids.NAME_ADD_BUTTON, "n_clicks"),
    State(ids.NAME_SEARCH_RESULTS_TABLE, "active_cell"),
    State(ids.NAME_SEARCH_RESULTS_TABLE, "data"),
    State(ids.NAME_ADDED_DROPDOWN, "value"),
    State(ids.NAME_ADDED_DROPDOWN, "options"),
    prevent_initial_call=True,
)
def add_name_to_dropdown(n_clicks, active_cell, data, value, options):
    if active_cell is None:
        return value, options

    selected_name = data[active_cell["row"]][DataSchema.NAME]
    value.append(selected_name)
    options.append(selected_name)
    return value, options


# # ------------- callback - update initial wages ----------------
@callback(
    Output(ids.INITIAL_WAGE_DROPDOWN, "value"),
    Output(ids.INITIAL_WAGE_INPUT, "value"),
    Output("initial-wage-accordion-item", "title"),
    Input(ids.INITIAL_WAGE_DROPDOWN, "value"),
    Input(ids.INITIAL_WAGE_INPUT, "value"),
    Input(ids.YEAR_RANGE_SLIDER, "value"),
    State("compensation-type-store", "data"),
    State("initial-wage-accordion-item", "title"),
    prevent_initial_call=True,
)
def update_initial_wage_input(
    dropdown_value, input_value, years, COMPENSATION_TYPE, intial_wage_title
):
    min_year = years[0]

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if (trigger_id == ids.INITIAL_WAGE_DROPDOWN) or (
        trigger_id == ids.YEAR_RANGE_SLIDER
    ):
        # if callback was triggered by user selecting from the dropdown menu, find the selected initial wage to display in the input field
        logical_array = (df_jobs[DataSchema.YEAR] == min_year) & (
            df_jobs[DataSchema.NAME] == dropdown_value
        )  # need to handle if more than 1 match
        if sum(logical_array) == 1:
            input_value = df_jobs.loc[logical_array, COMPENSATION_TYPE].iloc[0]
        else:
            input_value = ""  # default value if no string matches

    elif trigger_id == ids.INITIAL_WAGE_INPUT:
        # if callback was triggered by user editing the input field, set dropdown value to empty
        dropdown_value = ""
        input_value = input_value

    input_value = (
        input_value * 100
    )  # this is necessary because the raw files are divided by 100
    initial_wage_title = "Starting Compensation: $" + str(input_value)
    return dropdown_value, input_value, initial_wage_title


# ------------- callback - filtered-names-data -----------------
# triggered (1) when name is added/dropped or (2) year range slider is moved (3) initial creation of data store
# filters by names detected in dropdown menu and year range
@callback(
    Output("filtered-names-data", "data"),
    Input(ids.NAME_ADDED_DROPDOWN, "value"),
    # Input("compensation-accordion-item", "title"),  # why?
    Input("compensation-type-store", "data"),
    prevent_initial_call=True,
)
def filter_names_data(names, COMPENSATION_TYPE):

    if names is None:
        raise PreventUpdate

    # IMPORTANT when dealing with categories (cat.remove_unused_categories)
    if names == []:
        df_names_filtered = pd.DataFrame(
            columns=[COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]
        )
    else:
        logical_array = df_names[DataSchema.NAME].isin(names)
        df_names_filtered = df_names.loc[
            logical_array, [COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]
        ]
        # df_names_filtered = df_names_filtered.merge(df_names.loc[(df_names[DataSchema.NAME].isin(names)),DataSchema.NAME].cat.remove_unused_categories(),left_index=True, right_index=True)

    return df_names_filtered.to_json(orient="split")


# ------------- callback - filtered-jobs-data -----------------
# triggered (1) when name is added/dropped or (2) year range slider is moved
# filters by jobs detected in dropdown menu and year range
# prevent_initial_call is false because we want this to be updated ast startup
@callback(
    Output("filtered-jobs-data", "data"),
    Input(ids.RATE_JOB_DROPDOWN, "value"),
    Input(
        "filtered-names-data", "data"
    ),  # filtered names data triggers this chained callback
    State("compensation-type-store", "data"),
    prevent_initial_call=True,
)
def filter_jobs_data(jobs, df_names_filtered, COMPENSATION_TYPE):
    if jobs is None:
        raise PreventUpdate

    if df_names_filtered is not None:
        df_names_filtered = pd.read_json(df_names_filtered, orient="split")

    # IMPORTANT for mem usage when dealing with categories (cat.remove_unused_categories)
    logical_array = df_jobs[DataSchema.NAME].isin(jobs)
    df_jobs_filtered = df_jobs.loc[
        logical_array, [COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]
    ]
    # df_jobs_filtered = df_jobs_filtered.merge(df_jobs.loc[logical_array, DataSchema.NAME].cat.remove_unused_categories(),left_index=True, right_index=True)

    # combine
    df_jobs_filtered = pd.concat([df_jobs_filtered, df_names_filtered]).astype(
        {DataSchema.NAME: "category"}
    )

    return df_jobs_filtered.to_json(orient="split")


# ------------- callback - filtered-combined-data -----------------
#
# combines filtered-jobs-data and filtered-names-data
# further processing by handling duplicates,
@callback(
    Output("filtered-combined-data", "data"),
    # Output("year-range-accordion-item", "title"),
    Input("filtered-jobs-data", "data"),
    Input(ids.YEAR_RANGE_SLIDER, "value"),
    State("compensation-type-store", "data"),
    # State("year-range-accordion-item", "title"),
    prevent_initial_call=True,
)
def filter_combined_data(df_jobs_filtered, years, COMPENSATION_TYPE):

    df_jobs_filtered = pd.read_json(df_jobs_filtered, orient="split")
    min_year = years[0]
    max_year = years[1]

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == ids.YEAR_RANGE_SLIDER:
        year_range_accordion_title = (
            "Year Range: " + str(min_year) + "-" + str(max_year)
        )

    # df_jobs_filtered already contains names data if any
    df_combined = df_jobs_filtered

    # filter out unused years
    logical_array = (df_combined[DataSchema.YEAR] >= min_year) & (
        df_combined[DataSchema.YEAR] <= max_year
    )
    df_combined_filtered = df_combined.loc[
        logical_array, [COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]
    ]

    # handle duplicates (same year and name)
    # TODO: handle "duplicates" with common names
    df_duplicates = df_combined_filtered.loc[
        df_combined_filtered[[DataSchema.YEAR, DataSchema.NAME]].duplicated(keep=False),
        [COMPENSATION_TYPE, DataSchema.YEAR],
    ]  # grab all duplicates (names and year)
    if len(df_duplicates) > 0:
        df_duplicates = df_duplicates.merge(
            df_combined_filtered.loc[
                df_combined_filtered[[DataSchema.YEAR, DataSchema.NAME]].duplicated(
                    keep=False
                ),
                DataSchema.NAME,
            ].cat.remove_unused_categories(),
            left_index=True,
            right_index=True,
        )
        df_duplicates = (
            df_duplicates.groupby([DataSchema.YEAR, DataSchema.NAME])[COMPENSATION_TYPE]
            .sum()
            .reset_index()
        )  # add duplicates together
        df_duplicates = df_duplicates[
            df_duplicates[COMPENSATION_TYPE] != 0
        ]  # drop some rows with no values
        df_combined_filtered = df_combined_filtered[
            ~df_combined_filtered[[DataSchema.YEAR, DataSchema.NAME]].duplicated(
                keep=False
            )
        ]  # delete duplciates from dff_combined
        df_combined_filtered = pd.concat(
            [df_combined_filtered, df_duplicates]
        )  # concatenate together
        df_combined_filtered = df_combined_filtered.sort_values(
            by=[DataSchema.NAME, DataSchema.YEAR], ascending=True
        )

    # convert df_combined_filtered[COMPENSATION_TYPE] to uint32 and multiply by 100
    df_combined_filtered[COMPENSATION_TYPE] = (
        df_combined_filtered[COMPENSATION_TYPE].astype("uint32") * 100
    )

    return df_combined_filtered.to_json(orient="split")


# ----------------- function for resetting figures -----
def reset_fig_lollipop():

    fig_lollipop = go.Figure()

    # templates
    lollipop_template = go.layout.Template()
    lollipop_template.layout = go.Layout(
        paper_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        showlegend=False,
        title_font=dict(family="Arial", size=20),
        title_x=0,
        yaxis=dict(
            linewidth=1,
            linecolor="black",
            showgrid=True,
            gridcolor=colors.GRID_LINES_COLOR,
            gridwidth=1,
            automargin=True,
            showline=False,
            fixedrange=True,
        ),
        xaxis=dict(
            zeroline=False,
            rangemode="tozero",
            title=dict(text="Compensation (USD)"),
            showgrid=True,
            gridcolor=colors.GRID_LINES_COLOR,
            gridwidth=1,
            showline=True,
            linewidth=1,
            linecolor="black",
            fixedrange=True,
            automargin=True,
            title_standoff=15,
        ),
        margin=dict(autoexpand=True, r=0, t=0, b=40, l=10),
        dragmode=False,
    )
    fig_lollipop.update_layout(template=lollipop_template)

    return fig_lollipop


def reset_figures(real_wages_axis_type):

    fig_real_wages = go.Figure()
    fig_projected_wages = go.Figure()

    line_template = go.layout.Template()
    line_template.layout = go.Layout(
        paper_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        showlegend=False,
        title_font=dict(family="Arial", size=20),
        title_x=0,
        yaxis=dict(
            linewidth=1,
            linecolor="black",
            showgrid=True,
            gridcolor=colors.GRID_LINES_COLOR,
            gridwidth=1,
            automargin=True,
            showline=True,
            fixedrange=True,
            title_standoff=20,
        ),
        xaxis=dict(
            zeroline=False,
            showgrid=True,
            gridcolor=colors.GRID_LINES_COLOR,
            gridwidth=1,
            showline=True,
            linewidth=1,
            linecolor="black",
            dtick=1,
            fixedrange=True,
        ),
        margin=dict(autoexpand=True, r=0, t=0, b=40, l=40),
        hovermode="x",
        dragmode=False,
    )
    fig_real_wages.update_layout(
        template=line_template,
        yaxis_title_text="Compensation (USD)",
        yaxis_type=real_wages_axis_type,
    ),
    fig_projected_wages.update_layout(
        template=line_template, yaxis_title_text="Your Projected Compensation (USD)"
    )

    # create empty dataframes to track names of traces
    df_traces_in_real_wages = pd.DataFrame({DataSchema.NAME: [], "Index": []}).astype(
        {DataSchema.NAME: "category", "Index": int}
    )
    df_traces_in_projected_wages = pd.DataFrame(
        {DataSchema.NAME: [], "Index": []}
    ).astype({DataSchema.NAME: "category", "Index": int})

    return (
        fig_projected_wages,
        fig_real_wages,
        df_traces_in_projected_wages,
        df_traces_in_real_wages,
    )


# --------------- function for updating figures --------
# triggered when (1) filtered-jobs-data/filtered-names-data stores are updated
#
# this callback updates figs only by adding/"removing" traces ("not technically removing, just deleting variables")
# also maintains a data frame ledger that tracks what names/jobs currently have traces in the figs
@callback(
    Output("traces-in-real-wages", "data"),
    Output("traces-in-projected-wages", "data"),
    Output(ids.PROJECTED_WAGES_LINE_PLOT, "figure"),
    Output(ids.REAL_WAGES_LINE_PLOT, "figure"),
    Output(ids.LOLLIPOP_CHART, "figure"),
    Output("lollipop-chart-title", "children"),
    Input(ids.INITIAL_WAGE_INPUT, "value"),
    Input("filtered-combined-data", "data"),
    # Input("refresh-figures-button", "n_clicks"),
    Input("real-wages-scale-switch", "value"),
    State(ids.YEAR_RANGE_SLIDER, "value"),
    State("traces-in-real-wages", "data"),
    State("traces-in-projected-wages", "data"),
    State(ids.PROJECTED_WAGES_LINE_PLOT, "figure"),
    State(ids.REAL_WAGES_LINE_PLOT, "figure"),
    State(ids.LOLLIPOP_CHART, "figure"),
    State("compensation-type-store", "data"),
    prevent_initial_call=True,
)
def update_figures(
    initial_wage,
    df_combined_filtered,
    # n_clicks,
    real_wages_scale_switch_value,
    years,
    df_traces_in_real_wages,
    df_traces_in_projected_wages,
    fig_projected_wages,
    fig_real_wages,
    fig_lollipop,
    COMPENSATION_TYPE,
):
    t0 = time.time()
    df_combined_filtered = pd.read_json(df_combined_filtered, orient="split")

    if df_traces_in_real_wages is not None:
        df_traces_in_real_wages = pd.read_json(df_traces_in_real_wages, orient="split")

    if df_traces_in_projected_wages is not None:
        df_traces_in_projected_wages = pd.read_json(
            df_traces_in_projected_wages, orient="split"
        )

    min_year = years[0]
    max_year = years[1]
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if real_wages_scale_switch_value == True:
        real_wages_axis_type = "log"  # or linear
    else:  # default is linear even
        real_wages_axis_type = "linear"

    # if just the switch is pushed, only need to update the scale and don't do anything else
    if trigger_id == "real-wages-scale-switch":
        fig_real_wages["layout"]["yaxis"]["type"] = real_wages_axis_type
        lollipop_chart_title = title = "Years: " + str(min_year) + "-" + str(max_year)
        return (
            df_traces_in_real_wages.to_json(orient="split"),
            df_traces_in_projected_wages.to_json(orient="split"),
            fig_projected_wages,
            fig_real_wages,
            fig_lollipop,
            lollipop_chart_title,
        )

    # if no names/positions added, df_combined filtered is empty, so just reset plots:
    if len(df_combined_filtered) == 0:
        (
            fig_projected_wages,
            fig_real_wages,
            df_traces_in_projected_wages,
            df_traces_in_real_wages,
        ) = reset_figures(real_wages_axis_type)
        fig_lollipop = reset_fig_lollipop()
        lollipop_chart_title = title = "Years: " + str(min_year) + "-" + str(max_year)
        return (
            df_traces_in_real_wages.to_json(orient="split"),
            df_traces_in_projected_wages.to_json(orient="split"),
            fig_projected_wages,
            fig_real_wages,
            fig_lollipop,
            lollipop_chart_title,
        )

    # the innermost if statement should evaluate as true when user moves the year slider or modify input function; if so, resets plots and "ledgers"
    if fig_real_wages is not None:
        if fig_real_wages["layout"]["xaxis"]["range"] is not None:
            current_fig_min_year = -int(
                -fig_real_wages["layout"]["xaxis"]["range"][0] // 1
            )  # this rounds up b/c axes min is less than the smallest year
            current_fig_max_year = int(
                fig_real_wages["layout"]["xaxis"]["range"][1] // 1
            )  # this rounds down

            if (
                (current_fig_min_year != min_year)
                or (current_fig_max_year != max_year)
                or (trigger_id == ids.INITIAL_WAGE_INPUT)
            ):
                (
                    fig_projected_wages,
                    fig_real_wages,
                    df_traces_in_projected_wages,
                    df_traces_in_real_wages,
                ) = reset_figures(real_wages_axis_type)
                fig_lollipop = reset_fig_lollipop()
            else:
                # do not reset real/projected wages figs - build it from dictionaries from their existing state
                fig_real_wages = go.Figure(fig_real_wages)
                fig_projected_wages = go.Figure(fig_projected_wages)
                fig_lollipop = reset_fig_lollipop()

    # the very first invocation of this callback is from updating 'filtered-jobs-data', triggered by the modal closing
    if (
        (df_traces_in_real_wages is None)
        or (df_traces_in_projected_wages is None)
        or (trigger_id == "refresh-figures-button")
    ):
        reset_flag = False
        (
            fig_projected_wages,
            fig_real_wages,
            df_traces_in_projected_wages,
            df_traces_in_real_wages,
        ) = reset_figures(real_wages_axis_type)
        fig_lollipop = reset_fig_lollipop()

    # for real wages:
    # get names for real_wages figure
    names_wanted_in_real_wages = set(df_combined_filtered.loc[:, DataSchema.NAME])
    names_already_in_real_wages = set(df_traces_in_real_wages.loc[:, DataSchema.NAME])

    # names already in real wages but not in wanted: delete traces
    names_2delete_real_wages = list(
        names_already_in_real_wages.difference(names_wanted_in_real_wages)
    )
    logical_array = df_traces_in_real_wages[DataSchema.NAME].isin(
        names_2delete_real_wages
    )
    indexes_2delete_real_wages = df_traces_in_real_wages.loc[logical_array, "Index"]
    for i in indexes_2delete_real_wages:
        fig_real_wages.data[int(i)][
            "x"
        ] = []  # awkward, but can't delete from tuple; can hide/modify inside objects
        fig_real_wages.data[int(i)]["y"] = []

    df_traces_in_real_wages = df_traces_in_real_wages.loc[
        ~logical_array, :
    ]  # remove deleted traces from the df "ledger"

    # names in wanted but not yet in real wages: add traces
    names_2add_real_wages = list(
        names_wanted_in_real_wages.difference(names_already_in_real_wages)
    )
    fig_real_wage_indices = list()
    for name in names_2add_real_wages:
        logical_array = df_combined_filtered.loc[:, DataSchema.NAME] == name
        x_var = df_combined_filtered.loc[logical_array, DataSchema.YEAR]
        y_var = df_combined_filtered.loc[logical_array, COMPENSATION_TYPE]

        fig_real_wages.add_trace(
            go.Scatter(x=x_var, y=y_var, name=name, hovertemplate="$%{y}")
        )
        fig_real_wage_indices.append(len(fig_real_wages.data) - 1)

    df_traces_in_real_wages = pd.concat(
        [
            df_traces_in_real_wages,
            pd.DataFrame(
                {DataSchema.NAME: names_2add_real_wages, "Index": fig_real_wage_indices}
            ),
        ]
    ).astype(
        {DataSchema.NAME: "category", "Index": int}
    )  # update ledger

    # for projected wages/lollipop:
    # additional filter for names/jobs that do not span the years
    names_with_min = df_combined_filtered.loc[
        df_combined_filtered[DataSchema.YEAR] == min_year, DataSchema.NAME
    ]
    names_with_max = df_combined_filtered.loc[
        df_combined_filtered[DataSchema.YEAR] == max_year, DataSchema.NAME
    ]
    names_wanted_in_projected_wages = set(names_with_max) & set(names_with_min)
    names_already_in_projected_wages = set(
        df_traces_in_projected_wages.loc[:, DataSchema.NAME]
    )

    # names already in real wages but not in wanted: delete traces
    names_2delete_projected_wages = list(
        names_already_in_projected_wages.difference(names_wanted_in_projected_wages)
    )
    logical_array = df_traces_in_projected_wages[DataSchema.NAME].isin(
        names_2delete_projected_wages
    )
    indexes_2delete_projected_wages = df_traces_in_projected_wages.loc[
        logical_array, "Index"
    ]
    for i in indexes_2delete_projected_wages:
        fig_projected_wages.data[int(i)][
            "x"
        ] = []  # awkward, but can't delete from tuple; can hide/modify inside objects
        fig_projected_wages.data[int(i)]["y"] = []
    df_traces_in_projected_wages = df_traces_in_projected_wages.loc[
        ~logical_array, :
    ]  # remove deleted traces from the df "ledger"

    # names in wanted but not yet in real wages: add traces
    names_2add_projected_wages = list(
        names_wanted_in_projected_wages.difference(names_already_in_projected_wages)
    )
    fig_projected_wage_indices = list()
    for name in names_2add_projected_wages:
        logical_array = df_combined_filtered.loc[:, DataSchema.NAME] == name

        pay = df_combined_filtered.loc[logical_array, COMPENSATION_TYPE].to_numpy()
        priorpay = (
            df_combined_filtered.loc[logical_array, COMPENSATION_TYPE]
            .shift(1)
            .to_numpy()
        )
        priorpay[0] = pay[0]
        adjustment = (pay - priorpay) / priorpay + 1
        cumadjustment = pd.Series(adjustment).cumprod()

        y_var = round(
            cumadjustment * initial_wage, -2
        )  # round to 100s to clean up the hover text
        x_var = df_combined_filtered.loc[logical_array, DataSchema.YEAR]

        name = "at " + name + " rate"
        fig_projected_wages.add_trace(
            go.Scatter(x=x_var, y=y_var, hovertemplate="$%{y}", name=name)
        )
        fig_projected_wage_indices.append(len(fig_projected_wages.data) - 1)

    df_traces_in_projected_wages = pd.concat(
        [
            df_traces_in_projected_wages,
            pd.DataFrame(
                {
                    DataSchema.NAME: names_2add_projected_wages,
                    "Index": fig_projected_wage_indices,
                }
            ),
        ]
    ).astype(
        {DataSchema.NAME: "category", "Index": int}
    )  # update ledger
    projected_wages_chart_title = title = (
        "Years: " + str(min_year) + "-" + str(max_year)
    )

    # create df_lollipop (pivot_wider the first and last years)
    # df lollipop needs to be reset every time because of sorting by largest to smallest
    df_lollipop = df_combined_filtered[
        df_combined_filtered[DataSchema.NAME].isin(names_wanted_in_projected_wages)
    ]  # df lollipop uses the same wanted names as projected wages
    lollipop_chart_title = title = "Years: " + str(min_year) + "-" + str(max_year)
    if len(df_lollipop) > 0:
        df_lollipop = df_lollipop.pivot(
            index=DataSchema.NAME, columns=DataSchema.YEAR, values=COMPENSATION_TYPE
        ).reset_index()

        # sort by ascending wages
        df_lollipop = df_lollipop.sort_values(by=[max_year, min_year], ascending=True)

        lollipop_x_start = df_lollipop[min_year].tolist()
        lollipop_x_end = df_lollipop[max_year].tolist()
        lollipop_y = (
            df_lollipop[DataSchema.NAME].str.replace(" ", "<br>", n=1).tolist()
        )  # also add line break the first space to wrap text

        for i in range(0, len(lollipop_x_start)):
            fig_lollipop.add_trace(
                go.Scatter(
                    x=[lollipop_x_start[i], lollipop_x_end[i]],
                    y=[lollipop_y[i], lollipop_y[i]],
                    hoverinfo="skip",
                    line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=3),
                )
            )

        lollipop_marker_size = 9
        fig_lollipop.add_trace(
            go.Scatter(
                x=lollipop_x_start,
                y=lollipop_y,
                mode="markers",
                marker_symbol="circle",
                marker_size=lollipop_marker_size,
                hovertemplate="$%{x}<br>" + str(min_year) + "<extra></extra>",
                marker_color=colors.START_MARKER_COLOR,
            )
        )

        fig_lollipop.add_trace(
            go.Scatter(
                x=lollipop_x_end,
                y=lollipop_y,
                mode="markers",
                marker_size=lollipop_marker_size,
                hovertemplate="$%{x}<br>" + str(max_year) + "<extra></extra>",
                marker_color=colors.END_MARKER_COLOR,
            )
        )

        if len(lollipop_y) < 6:
            fig_lollipop.update_layout(height=400)
        else:
            fig_lollipop.update_layout(
                height=(len(lollipop_y) - 6) * 50
                + 400  # increase height by 30px for each additional person past 5
            )
    print("figure update: " + str(time.time() - t0))
    return (
        df_traces_in_real_wages.to_json(orient="split"),
        df_traces_in_projected_wages.to_json(orient="split"),
        fig_projected_wages,
        fig_real_wages,
        fig_lollipop,
        lollipop_chart_title,
    )
