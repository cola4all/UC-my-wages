from dash import callback_context as ctx
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc, dash_table, ServersideOutput, ServersideOutputTransform
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os, pathlib
import time

app = DashProxy(__name__, transforms=[ServersideOutputTransform()], external_stylesheets=[dbc.themes.FLATLY], assets_folder='assets',
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

# define paths
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
JOB_DATA_PATH =  os.path.join(APP_PATH, "assets", "salaries_by_job.parquet")
NAME_DATA_PATH =  os.path.join(APP_PATH, "assets", "salaries_by_name.parquet")
PROPOSAL_DATA_PATH = os.path.join(APP_PATH, "assets", "wage_proposals.csv")

# create schemas so that you don't need to remember the labels when coding
class DataSchema:
    NAME = "Employee Name"
    JOB = "Job Title"
    JOB_ABBREVIATED = "Abbreviated Job Title"
    TOTAL_PAY = 'Total Pay'
    TOTAL_PAY_AND_BENEFITS = 'Total Pay & Benefits'
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
    INITIAL_WAGE_CONTAINER = 'initial-wage-container'
    PROPOSAL_LOLLIPOP_PLOT = 'proposal-lollipop-plot'

class colors:
    PLOT_BACKGROUND_COLOR = "#edeff1"
    END_MARKER_COLOR = "#355218"
    START_MARKER_COLOR = "#759356"
    LOLLIPOP_LINE_COLOR = "#7B7B7B"
    GRID_LINES_COLOR = "#C5CCCA"


t0 = time.time()
print('reading csv 1:')
# load data
df_jobs = pd.read_parquet(JOB_DATA_PATH, engine='fastparquet')     # need to create parquet file first

# df_jobs = pd.read_csv(JOB_DATA_PATH, 
#     usecols=[
#         DataSchema.NAME,
#         DataSchema.TOTAL_PAY,
#         DataSchema.TOTAL_PAY_AND_BENEFITS,
#         DataSchema.YEAR],         # this col is used for sorting by names
#     dtype={
#         DataSchema.NAME: "category",
#         DataSchema.TOTAL_PAY: float,
#         DataSchema.TOTAL_PAY_AND_BENEFITS: float,
#         DataSchema.YEAR: cat_type_year
#     }
# )
print(time.time() - t0)

t0 = time.time()
print('reading csv 2:')
df_names = pd.read_parquet(NAME_DATA_PATH, engine='fastparquet')
print(time.time() - t0)

print('size of df_names_filtered:')
print(df_names.info(memory_usage = 'deep'))

t0 = time.time()



t0 = time.time()
print('reading csv 3:')
df_proposal = pd.read_csv(PROPOSAL_DATA_PATH)
print(time.time() - t0)

print('size of df_names_filtered:')
print(df_proposal.info(memory_usage = 'deep'))



fig_proposal = go.Figure()

# templates
proposal_template = go.layout.Template()
proposal_template.layout = go.Layout(
        paper_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        showlegend=True,
        title_font=dict(family="Arial", size=20),
        title_x=0,
        yaxis=dict(linewidth=1, linecolor = "black", 
            showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
            automargin =True,
            showline = False,
            fixedrange = True
        ),
        xaxis=dict(zeroline = False, rangemode = "tozero", 
            title = dict(text = "Base Pay (USD)"),
            showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
            showline = True, linewidth=1, linecolor = "black",
            fixedrange = True, automargin = True,
            title_standoff = 15,
        ),
        margin = dict(autoexpand = True, r=0, t=0, b=40, l=10),
        dragmode = False,

        
    )
fig_proposal.update_layout(template=proposal_template, 
    legend= dict(
        yanchor="bottom", 
        y=1.02,    
        xanchor="center",
        x=0.5,
        orientation='h'))

t0 = time.time()
# create the static proposal plot
df_proposal = df_proposal.iloc[::-1]       # reverses order of df
proposal_x_current = df_proposal['Current'].tolist()
proposal_x_uc_dec2 = df_proposal['UC Proposal (Dec 2)'].tolist()
proposal_x_uc_dec15 = df_proposal['UC Mediated Proposal (Dec 15)'].tolist()
proposal_x_sru_dec8 = df_proposal['SRU/ASE Proposal (Dec 8)'].tolist()  
proposal_x_sru_nov30 = df_proposal['SRU/ASE Proposal (Nov 30)'].tolist()  
proposal_x_sru_nov14 = df_proposal['SRU/ASE Proposal (Nov 14)'].tolist()  
proposal_y = df_proposal['Position'].str.replace(' ','<br>', n=1).tolist()      # also add line break the first space to wrap text


# colors
uc_dec2_dot_color = "#6FA7C0"
uc_dec15_dot_color = "#005581"
current_dot_color = "#616161"
sru_dec8_color = "#FF366A"
sru_nov30_dot_color =  "#E1839C"
sru_nov14_dot_color = "#EAABBC"

proposal_marker_size = 7
                
for i in range(0, len(proposal_x_sru_nov30)):         
    fig_proposal.add_trace(go.Scatter(
                showlegend=False,
                x = [proposal_x_sru_dec8[i], proposal_x_sru_nov14[i]],
                y = [proposal_y[i],proposal_y[i]],
                hoverinfo='skip',
                line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=2, dash='dot')))

for i in range(0, len(proposal_x_sru_dec8)):             # this skips the last two missing from uaw
    fig_proposal.add_trace(go.Scatter(
                showlegend=False,
                x = [proposal_x_uc_dec15[i], proposal_x_sru_dec8[i]],
                y = [proposal_y[i],proposal_y[i]],
                hoverinfo='skip',
                line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=2)))

for i in range(0, len(proposal_x_current)):         
    fig_proposal.add_trace(go.Scatter(
                showlegend=False,
                x = [proposal_x_current[i], proposal_x_uc_dec15[i]],
                y = [proposal_y[i],proposal_y[i]],
                hoverinfo='skip',
                line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=2, dash='dot')))


fig_proposal.add_trace(go.Scatter(
                name='Current Base Pay',
                x=proposal_x_current,
                y=proposal_y,
                mode = "markers",
                marker_symbol = "circle",
                marker_size = proposal_marker_size,
                hovertemplate = 'Current:<br>$%{x:,.2f}<extra>%{y}</extra>',
                marker_color=current_dot_color,
            )
)

fig_proposal.add_trace(go.Scatter(
                name='UC (Dec 2)',
                x=proposal_x_uc_dec2,
                y=proposal_y,
                mode = "markers",
                marker_size = proposal_marker_size,
                hovertemplate = 'UC (Dec 2):<br>$%{x:,.2f}<extra>%{y}</extra>',
                marker_color=uc_dec2_dot_color)
)

fig_proposal.add_trace(go.Scatter(
                name='UC Mediated (Dec 15)',
                x=proposal_x_uc_dec15,
                y=proposal_y,
                mode = "markers",
                marker_size = proposal_marker_size,
                hovertemplate = 'UC Mediated (Dec 15):<br>$%{x:,.2f}<extra>%{y}</extra>',
                marker_color=uc_dec15_dot_color)
)

fig_proposal.add_trace(go.Scatter(
                name='SRU/ASE (Nov 14)',
                x=proposal_x_sru_nov14,
                y=proposal_y,
                mode = "markers",
                marker_size = proposal_marker_size,
                hovertemplate = 'SRU/ASE (Nov 14):<br>$%{x:,.2f}<extra>%{y}</extra>',
                marker_color=sru_nov14_dot_color)
)

fig_proposal.add_trace(go.Scatter(
                name='SRU/ASE (Nov 30)',
                x=proposal_x_sru_nov30,
                y=proposal_y,
                mode = "markers",
                marker_size = proposal_marker_size,
                hovertemplate = 'SRU/ASE (Nov 30):<br>$%{x:,.2f}<extra>%{y}</extra>',
                marker_color=sru_nov30_dot_color)
)

fig_proposal.add_trace(go.Scatter(
                name='SRU/ASE (Dec 8)',
                x=proposal_x_sru_dec8,
                y=proposal_y,
                mode = "markers",
                marker_size = proposal_marker_size,
                hovertemplate = 'SRU/ASE (Dec 8):<br>$%{x:,.2f}<extra>%{y}</extra>',
                marker_color=sru_dec8_color)
)

if len(proposal_y) < 6:
    fig_proposal.update_layout(height = 400)
else:
    fig_proposal.update_layout(height = (len(proposal_y)-6)*50+400)            # increase height by 30px for each additional person past 5



cat_type_year = pd.api.types.CategoricalDtype(categories=[2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021], ordered=True)
df_jobs['Year'] = df_jobs['Year'].astype(cat_type_year)
df_names['Year'] = df_names['Year'].astype(cat_type_year)

# t0 = time.time()
print('creating html components:')
# ------------- create html components --------------------
# better way to do this? this is faster than reading a df
unique_jobs = df_jobs['Employee Name'].unique().tolist()

job_container = html.Div(
    children = [
        html.P("Select a position to add to the plots:", id="job-label"),
        dcc.Dropdown(
            id=ids.RATE_JOB_DROPDOWN,
            options=unique_jobs,
            value=['GSR (Step 5)', 'Teaching Assistant', 'Assistant Professor (II)', 'Associate Professor (II)', 'Professor (II)'],
            multi=True
        )
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

# ------------- create year range slider components ----------------
year_range_slider = dcc.RangeSlider(
            min = 2011, 
            max = 2021, 
            step = 1,
            value = [2011, 2021],
            marks = {
                2011: '2011',
                2012: '2012',
                2013: '2013',
                2014: '2014',
                2015: '2015',
                2016: '2016',
                2017: '2017',
                2018: '2018',
                2019: '2019',
                2020: '2020',
                2021: '2021'
            },
            id = ids.YEAR_RANGE_SLIDER
        )


# ------------- create name search components ----------------
name_search_container = dbc.Col(
    dbc.InputGroup(
        id = ids.NAME_SEARCH_CONTAINER,
        children = [
            dbc.InputGroupText('Enter name:',id='enter-name-text'),
            dbc.Input(id = ids.NAME_SEARCH_INPUT),
            dbc.Button('Search', id = ids.NAME_SEARCH_BUTTON, className='button')
        ],
    ),
    id='name_search_container',
    xxl = 4, xl = 5, lg = 6, md = 9, sm = 12
)

name_search_results_container = html.Div(
    id = ids.NAME_SEARCH_RESULTS_CONTAINER,
    children = [
        dash_table.DataTable(id = ids.NAME_SEARCH_RESULTS_TABLE),
    ]
)

name_add_container = html.Div(
    id = ids.NAME_ADD_CONTAINER,
    children = [
        dbc.Button('Add Selected Name', id = ids.NAME_ADD_BUTTON, className = 'button'),
        dcc.Dropdown(id = ids.NAME_ADDED_DROPDOWN,
            value = [],
            options = [],
            multi=True)
    ]
)



navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.NavbarBrand("UC My Wages", style={"font-size": "1.5rem"}),
                href="#",
                style={"textDecoration": "none"},
            )
        ],
        id="navbar-brand-container"
    ),
    color="#005581",
    dark=True,
    sticky='top',
    className = "navbar"
)

t0 = time.time()
print('creating layout:')

# create layout
app.layout = html.Div(
    className="app-div",
    children =[
        # html.Header(
        #     className = "title-container",
        #     children=[
        #         html.H2(app.title)
        #     ]
        # ),
        navbar,
        html.Div(
        className="content-div",
        children=[
            # data stores
            dcc.Store(id='filtered-names-data'),
            dcc.Store(id='filtered-jobs-data'),
            dcc.Store(id='filtered-combined-data'),
            dcc.Store(id='jobs-data'),
            dcc.Store(id='names-data'),
            dcc.Store(id='table-data-records-list'),
            dcc.Store(id='traces-in-real-wages'),
            dcc.Store(id='traces-in-projected-wages'),
            dcc.Store(id='compensation-type-store'),
            dcc.Interval(id='page-load-interval', n_intervals=0, max_intervals=0, interval=1), # max_intervals = 0 ensures callback only runs once at startup
            html.H4('UAW vs UC Base Pay Proposals'),
            dcc.Graph(id=ids.PROPOSAL_LOLLIPOP_PLOT, figure=fig_proposal, config={'displayModeBar': False}),
            html.P(),
            html.P('These base pays would be effective starting Oct 2023 and assume a 12-month appointment.'),
            html.P("Current data reflects proposals from Dec 8 (UAW) and Dec 15 (UC). We will be updating the tracker as proposed wages are verified."),
            dcc.Markdown("This plot aims to visualize the movement on a central bargaining issue over the course of negotiations between the two bargaining parties."),
            dcc.Markdown("As a disclaimer, the data used in the visualization summarizes base wage proposals using information that is most generalizable across all grad workers. The visualization does not reflect details like campus-based adjustments and new experience-based increments. For complete proposal details, please see the bargaining update documents from [FairUCNow](https://www.fairucnow.org/bargaining/)."),
            html.Hr(),
            html.H4('How does your compensation stack up against other UC employees?'),
            dcc.Markdown('Select a position from the options below or searching for an employee by name to add to the plot. Hover or click on a data point to compare across all employees for that year.'),
            dbc.Accordion(
                children = [
                    dbc.AccordionItem(
                        children = [
                            html.P('Select one of the following options:'),
                            dbc.Row(
                                children = [
                                    dbc.Col(dcc.Dropdown(
                                        options = ['Total Pay & Benefits', 'Total Pay'],
                                        value = 'Total Pay',
                                        multi=False,
                                        clearable = False,
                                        id = 'select-compensation-dropdown'
                                    ), lg=4, xl=3),
                                    dbc.Col(dbc.Button('Refresh Figures', id = 'refresh-figures-button', className='button')), 
                                ],
                                justify='center',
                                className="g-0"
                            )
                        ],
                        title = 'Selected Compensation: Total Pay',
                        id = 'compensation-accordion-item'
                    ),
                    dbc.AccordionItem(
                        children = [
                            job_container,
                        ],
                        title = 'Compare Positions',
                        id = 'compare-jobs-accordion-item'
                    ),
                    dbc.AccordionItem(
                        children = [
                            dcc.Loading(
                                    id = 'name-container',
                                    children = [
                                        name_search_container,
                                        html.P(),
                                        name_search_results_container,
                                        name_add_container
                                    ]
                                
                            ),
                        ],
                        title = 'Compare Employees'
                    )
                ],
                id = 'top-accordion',
                always_open = True,
                active_item = ['item-1', 'item-2']    # this needs to be string id (not assigned id, which starts at 0)
            ),
            html.Div([
                    html.P(),
                    dbc.Row(
                        [
                            dbc.Col(dbc.Label("linear"), className="pe-2"),
                            dbc.Col(dbc.Switch(value = False, id='real-wages-scale-switch'), className="p-0"),
                            dbc.Col(dbc.Label("log"), className="p-0"),
                        ],
                    className="d-inline-flex g-0 align-items-start",
                    ),
                ]
            ),
            dcc.Graph(id=ids.REAL_WAGES_LINE_PLOT, config={'displayModeBar': False}, figure={'layout': {'autosize': True, 'fillframe': True}}),
            html.Hr(),
            html.H4('Ever wonder what your compensation might be if it grew at the same rate as your peers, employees, or bosses?'), 
            dcc.Markdown('This plot projects how your specified starting compensation would change if you received the same year-to-year percentage-based raises as other employees. *Simply set your starting compensation below. You may also need to adjust the year range slider (this rescales the x-axis) to fit the range of years for which the employee has data.*'),
            dbc.Accordion(
                children=[
                    dbc.AccordionItem(
                        children = [
                            html.P('Set a starting compensation by selecting a job or entering a custom amount:'),
                            dcc.Dropdown(
                                id=ids.INITIAL_WAGE_DROPDOWN,
                                options=unique_jobs,
                                value = "GSR (Step 5)",
                                placeholder="Set an starting compensation based on job or enter custom value on the right",
                                multi=False,
                                clearable=False
                            ),
                            dcc.Input(
                                id=ids.INITIAL_WAGE_INPUT, 
                                value = 22900, #old code: value = df_jobs.loc[(df_jobs[DataSchema.NAME]=="GSR (Step 1)") & (df_jobs[DataSchema.YEAR]==2011), DataSchema.PAY].iloc[0],
                                type="number", 
                                placeholder="",
                                debounce=True
                            ),
                        ],
                        title = 'Starting Compensation: $' + str(16698),
                        id = 'initial-wage-accordion-item'
                    ),
                    dbc.AccordionItem(
                        children = [
                            year_range_slider,
                        ],
                        title = 'Year Range: 2011-2021',
                        id = 'year-range-accordion-item'
                    ),
                ],
                always_open = True,
                active_item = ['item-0', 'item-1'],    # this needs to be string id (not assigned id, which starts at 0)
                id = 'bottom-accordion'
            ),
            dcc.Graph(id=ids.PROJECTED_WAGES_LINE_PLOT, config={'displayModeBar': False}),
            html.Hr(),
            html.H4('How do your raises compare in terms of the absolute dollar amount?'), 
            dcc.Markdown("We tend to talk about year-to-year raises in terms of percentages, but this obscures the fact that our **absolute wage growth** depends on this percentage **as well as our prior year's salary.** Tying our raises to our prior year's salary is great for high-income earners, but not so much for low-income workers. **This system locks lower-paid positions out of real wage growth, puts workers at the mercy of unpredictable rises in cost of living, and exacerabates income disparities between higher-paid executives and lower-paid workers.**"),
            dcc.Markdown("See how this disparity plays out in the UC system by comparing higher-paid employees to lower-paid employees in the following plot. The length of each line conveys a sense of the employee's raise over the provided year range. The further to the right, the more the employee earns."),
            dcc.Markdown("*If an employee that you added is missing from the plot, adjust the year range slider (above) to match the years for which that employee has data.*"),
            html.H5('Years: 2011-2021', id='lollipop-chart-title'),
            dcc.Graph(id=ids.LOLLIPOP_CHART, config={'displayModeBar': False}),
            html.Hr(),
            dbc.Accordion(
                children = [
                    dbc.AccordionItem(
                        children = [
                            dcc.Markdown("Data for UC employee wages are publicly available and retrieved from [Transparent California](https://transparentcalifornia.com/salaries/2021/university-of-california/)."),
                            dcc.Markdown("Graduate student research (GSR) pay scales from 2011-2021 are retrieved from [here](https://grad.ucsd.edu/financial/employment/student-pay-rates.html)."),
                            dcc.Markdown("Professor pay scales from 2011-2021 are retrieved from [here](https://ap.uci.edu/compensation/salary-scales/)."),
                        ],
                        title = 'Data Sources'
                    ),
                    dbc.AccordionItem(
                        children = [
                            dcc.Markdown("**This project is an active work in progress.** We are making this tool available to the public in its current state because of its relevance to the ongoing labor dispute between the UC and its 48,000 Academic Workers. It is our hope that this project helps the UC on its commitment to [Accountability and Transparency](https://ucannualwage.ucop.edu/wage/)."),
                            dcc.Markdown("The following are some limitations and features on our to-do list:"),
                            dcc.Markdown('''
                                * Currently, the app is unable to distinguish between employees who share the same name. The app currently aggregates all employees of the same name for a given year. A future release will be able to distinguish these employees.
                                * Employees making under $30K were removed from the current database. These may be added back in in the future.
                                * Improving the speed of generating new plots
                                * Streamlining the UI and making it more mobile-friendly and responsive across all screen sizes
                                * Creating a more robust pattern-matching for the employee name search
                                * Adding reference lines like Cost of Living for different cities to the plots
                                * Additional visualizations may be added in the future.
                            '''),
                            dcc.Markdown("Please [DM us on twitter](https://twitter.com/collthinking420) if you wish to report any bugs or feature requests."),                       
                        ],
                        title = 'Limitations and Future Releases'
                    )
                ],
                active_item=[]
            ),
            html.Hr(),
            dcc.Markdown('''##### **[#UCMyWages](https://twitter.com/search?q=UCMyWages&src=typeahead_click&f=top)**'''),
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
                centered=True

            )
        ]
    )
    ]
)

print(time.time() - t0)
#--------------- callback - dropdown -------
# also - dsiable/enable refresh plot
@app.callback(
    ServersideOutput('compensation-type-store', 'data'),
    Output('compensation-accordion-item','title'),
    Input('select-compensation-dropdown','value'),
    prevent_initial_call = True,       # want to load in background
)
def save_datastore(compensation_type):

    compensation_type = ''.join(compensation_type)        # coerce a list to string
    
    if compensation_type is None:
        raise PreventUpdate

    #DataSchema.PAY = compensation_type      # bad: changing global variable interferes if two instances are run on one server
        
    title = 'Type of Compensation: ' + compensation_type

    return compensation_type, title

#--------------- callback - close modal -------
# triggered by pressing the close button
@app.callback(
    Output("landing-modal", "is_open"),
    Input("close-modal-button", "n_clicks"),
    prevent_initial_call = True
)
def close_modal(n_clicks): 
    return False

# ------------- callback - save_datastore ----------------------
# triggered by landing modal changing
@app.callback(
    ServersideOutput("jobs-data", "data"), 
    ServersideOutput("names-data",'data'),
    Output('select-compensation-dropdown', 'value'),
    Input('page-load-interval', 'n_intervals'),
    State('jobs-data', 'data'),
    State('names-data', 'data'),
    State('select-compensation-dropdown', 'value'),
    blocking = True, 
    prevent_initial_call = False)
def save_datastore(n_intervals, jobs_data, names_data, COMPENSATION_TYPE):
    if COMPENSATION_TYPE is None:
        COMPENSATION_TYPE = 'Total Pay'     # sets default COMPENSATION_TYPE here
    
    # names_data can be filtered by year? and earnings?
    if (jobs_data is None) and (names_data is None):
        return df_jobs, df_names, COMPENSATION_TYPE
    else:
        raise PreventUpdate
    
# ------------- callback - search names in data frame ----------------
@app.callback(
    Output(ids.NAME_SEARCH_RESULTS_CONTAINER, 'children'),
    Input(ids.NAME_SEARCH_BUTTON, 'n_clicks'),
    State(ids.NAME_SEARCH_INPUT, "value"),
    State('names-data','data'),
    prevent_initial_call=True,
    memoize = True,
    blocking = True,
)
def search_names(n_clicks, search_name, dff_names):
    print('entered search_names:')
    print(search_name)
    t0=time.time()
    # handle if names is empty
    if (search_name is None) or (dff_names is None):
        raise PreventUpdate
    # handle if no matches (maybe no need)

    # display unique matches
    df_names_match = dff_names[dff_names.loc[:,DataSchema.NAME].str.contains(search_name.casefold().strip(), regex=False)]
    print('pandas str contains:')
    print(time.time() - t0)

    t0=time.time()
    unique_names_match = list(set(df_names_match[DataSchema.NAME]))

    # handle if too many matches (todo: leave message)
    if len(unique_names_match) > 200:
        too_many_matches = html.Div(
            children = [
                html.Label('Found too many matching results. Please enter a more specific name.'),
            ]
        )
        return too_many_matches

    # build df where each row is a unique employee w/ an employee name col and a years available col
    table_data_records_list = []
    for name in unique_names_match:
        years_available = df_names_match[DataSchema.YEAR].loc[df_names_match[DataSchema.NAME]==name].to_list()
        years_available_str = ', '.join([str(x) for x in years_available])
        table_data_records_list.append({
            DataSchema.NAME: name, 
            'Years Available': years_available_str
        })
    print('rest of the script:')
    print(time.time() - t0)   

    name_search_results_container_updated = html.Div(
        children = [
            html.Label('Select a name to add to the plots'),
            dash_table.DataTable(
                data = table_data_records_list, 
                columns = [{"name": DataSchema.NAME, "id": DataSchema.NAME}, {"name": 'Years Available', "id": 'Years Available'}],
                active_cell = {'column': 0, 'row': 0},
                selected_cells = [{'column': 0, 'row': 0}],
                id = ids.NAME_SEARCH_RESULTS_TABLE
            )
        ]
    )
    return name_search_results_container_updated

# ------------- callback - add selected name from table to the dropdown ----------------
@app.callback(
    Output(ids.NAME_ADDED_DROPDOWN, "value"),
    Output(ids.NAME_ADDED_DROPDOWN, "options"),
    Input(ids.NAME_ADD_BUTTON, "n_clicks"),
    State(ids.NAME_SEARCH_RESULTS_TABLE, "active_cell"),
    State(ids.NAME_SEARCH_RESULTS_TABLE, "data"),
    State(ids.NAME_ADDED_DROPDOWN, "value"),
    State(ids.NAME_ADDED_DROPDOWN, "options"),
    prevent_initial_call=True,
    blocking = True,
)
def add_name_to_dropdown(n_clicks, active_cell, data, value, options):
    if active_cell is None:
        return value, options

    selected_name = data[active_cell['row']][DataSchema.NAME]
    value.append(selected_name)
    options.append(selected_name)
    return value, options

# ------------- callback - update initial wages ----------------
@app.callback(
    Output(ids.INITIAL_WAGE_DROPDOWN, "value"),
    Output(ids.INITIAL_WAGE_INPUT, "value"),
    Output('initial-wage-accordion-item', 'title'),
    Input(ids.INITIAL_WAGE_DROPDOWN, "value"),
    Input(ids.INITIAL_WAGE_INPUT, "value"),
    Input(ids.YEAR_RANGE_SLIDER, 'value'),
    State('jobs-data','data'),
    State('compensation-type-store','data'),
    State('initial-wage-accordion-item',  'title'),
    prevent_initial_call=True
)
def update_initial_wage_input(dropdown_value, input_value, years, df_jobs, COMPENSATION_TYPE, intial_wage_title):
    min_year = years[0]

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if (trigger_id == ids.INITIAL_WAGE_DROPDOWN) or (trigger_id == ids.YEAR_RANGE_SLIDER):
        # if callback was triggered by user selecting from the dropdown menu, find the selected initial wage to display in the input field
        logical_array = (df_jobs[DataSchema.YEAR] == min_year) & (df_jobs[DataSchema.NAME] == dropdown_value)  # need to handle if more than 1 match
        if sum(logical_array) == 1: 
            input_value = df_jobs.loc[logical_array, COMPENSATION_TYPE].iloc[0]  
        else:
            input_value = "" # default value if no string matches

    elif trigger_id == ids.INITIAL_WAGE_INPUT:
        # if callback was triggered by user editing the input field, set dropdown value to empty
        dropdown_value = ""
        input_value = input_value

    input_value = input_value*100   # this is necessary because the raw files are divided by 100
    initial_wage_title = 'Starting Compensation: $' + str(input_value)
    return dropdown_value, input_value, initial_wage_title

#------------- callback - filtered-names-data -----------------
# triggered (1) when name is added/dropped or (2) year range slider is moved (3) initial creation of data store
# filters by names detected in dropdown menu and year range
@app.callback(
    ServersideOutput('filtered-names-data', 'data'),
    Input(ids.NAME_ADDED_DROPDOWN, "value"),
    Input('names-data','data'),
    Input('compensation-accordion-item','title'),       # why?
    State('compensation-type-store', 'data'),
    prevent_initial_call = True
)
def filter_names_data(names, df_names, title, COMPENSATION_TYPE):

    if (names is None):
        raise PreventUpdate

    # IMPORTANT when dealing with categories (cat.remove_unused_categories)
    if names == []:
        df_names_filtered = pd.DataFrame(columns = [COMPENSATION_TYPE,DataSchema.YEAR, DataSchema.NAME])
    else:
        logical_array = (df_names[DataSchema.NAME].isin(names))
        df_names_filtered = df_names.loc[logical_array, [COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]]
        #df_names_filtered = df_names_filtered.merge(df_names.loc[(df_names[DataSchema.NAME].isin(names)),DataSchema.NAME].cat.remove_unused_categories(),left_index=True, right_index=True)

    return df_names_filtered

#------------- callback - filtered-jobs-data -----------------
# triggered (1) when name is added/dropped or (2) year range slider is moved
# filters by jobs detected in dropdown menu and year range
# prevent_initial_call is false because we want this to be updated ast startup
@app.callback(
    ServersideOutput('filtered-jobs-data', 'data'),
    Input(ids.RATE_JOB_DROPDOWN, "value"),
    Input('filtered-names-data','data'),            # filtered names data triggers this chained callback
    #Input('refresh-figures-button', 'n_clicks'),
    State('jobs-data','data'),
    State('compensation-type-store', 'data'),
    #Input('compensation-accordion-item','title'),
    prevent_initial_call = True
)
def filter_jobs_data(jobs, df_names_filtered, df_jobs, COMPENSATION_TYPE):

    if jobs is None:
        raise PreventUpdate

    # IMPORTANT for mem usage when dealing with categories (cat.remove_unused_categories)
    logical_array = (df_jobs[DataSchema.NAME].isin(jobs)) 
    df_jobs_filtered = df_jobs.loc[logical_array, [COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]]
    #df_jobs_filtered = df_jobs_filtered.merge(df_jobs.loc[logical_array, DataSchema.NAME].cat.remove_unused_categories(),left_index=True, right_index=True)

    # combine
    df_jobs_filtered= pd.concat([df_jobs_filtered, df_names_filtered]).astype({DataSchema.NAME: "category"})

    return df_jobs_filtered

#------------- callback - filtered-combined-data -----------------
#
# combines filtered-jobs-data and filtered-names-data
# further processing by handling duplicates, 
@app.callback(
    ServersideOutput('filtered-combined-data', 'data'),
    Output('year-range-accordion-item','title'),
    Input('filtered-jobs-data','data'),
    Input(ids.YEAR_RANGE_SLIDER, 'value'),
    State('compensation-type-store', 'data'),
    State('year-range-accordion-item','title'),
    prevent_initial_call = True
)
def filter_combined_data(df_jobs_filtered, years, COMPENSATION_TYPE, year_range_accordion_title):

    min_year = years[0]
    max_year = years[1]

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == ids.YEAR_RANGE_SLIDER:
        year_range_accordion_title = 'Year Range: ' + str(min_year) + '-' + str(max_year)

    # df_jobs_filtered already contains names data if any
    df_combined = df_jobs_filtered

    # filter out unused years
    logical_array = (df_combined[DataSchema.YEAR] >= min_year) & (df_combined[DataSchema.YEAR] <= max_year)
    df_combined_filtered = df_combined.loc[logical_array, [COMPENSATION_TYPE, DataSchema.YEAR, DataSchema.NAME]]
    
    # handle duplicates (same year and name)
    # TODO: handle "duplicates" with common names
    df_duplicates = df_combined_filtered.loc[df_combined_filtered[[DataSchema.YEAR, DataSchema.NAME]].duplicated(keep=False), [COMPENSATION_TYPE, DataSchema.YEAR]]                 # grab all duplicates (names and year)
    if len(df_duplicates) > 0:
        df_duplicates = df_duplicates.merge(df_combined_filtered.loc[df_combined_filtered[[DataSchema.YEAR, DataSchema.NAME]].duplicated(keep=False), DataSchema.NAME].cat.remove_unused_categories(), left_index=True, right_index=True)
        df_duplicates = df_duplicates.groupby([DataSchema.YEAR, DataSchema.NAME])[COMPENSATION_TYPE].sum().reset_index()       # add duplicates together
        df_duplicates = df_duplicates[df_duplicates[COMPENSATION_TYPE] != 0]      # drop some rows with no values
        df_combined_filtered = df_combined_filtered[~df_combined_filtered[[DataSchema.YEAR, DataSchema.NAME]].duplicated(keep=False)]                  # delete duplciates from dff_combined
        df_combined_filtered = pd.concat([df_combined_filtered, df_duplicates])                                                               # concatenate together
        df_combined_filtered = df_combined_filtered.sort_values(by=[DataSchema.NAME, DataSchema.YEAR], ascending=True)

    # convert df_combined_filtered[COMPENSATION_TYPE] to uint32 and multiply by 100
    df_combined_filtered[COMPENSATION_TYPE] = df_combined_filtered[COMPENSATION_TYPE].astype('uint32')*100

    return df_combined_filtered, year_range_accordion_title

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
            yaxis=dict(linewidth=1, linecolor = "black", 
                showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
                automargin =True,
                showline = False,
                fixedrange = True
            ),
            xaxis=dict(zeroline = False, rangemode = "tozero", 
                title = dict(text = "Compensation (USD)"),
                showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
                showline = True, linewidth=1, linecolor = "black",
                fixedrange = True, automargin = True,
                title_standoff = 15,
            ),
            margin = dict(autoexpand = True, r=0, t=0, b=40, l=10),
            dragmode = False
            
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
            yaxis=dict(linewidth=1, linecolor = "black", 
                showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
                automargin = True,
                showline = True,
                fixedrange = True,
                title_standoff = 20),
            xaxis=dict(zeroline = False,
                showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
                showline = True, linewidth=1, linecolor = "black",
                dtick = 1,
                fixedrange = True
                ),
            margin = dict(autoexpand = True, r=0, t=0, b=40, l=40),
            hovermode="x",
            dragmode = False
        )
    fig_real_wages.update_layout(template=line_template, yaxis_title_text = "Compensation (USD)", yaxis_type = real_wages_axis_type),
    fig_projected_wages.update_layout(template=line_template, yaxis_title_text = "Your Projected Compensation (USD)")

    # create empty dataframes to track names of traces
    df_traces_in_real_wages = pd.DataFrame({DataSchema.NAME: [], "Index": []}).astype({DataSchema.NAME: "category", "Index": int})
    df_traces_in_projected_wages = pd.DataFrame({DataSchema.NAME: [], "Index": []}).astype({DataSchema.NAME: "category", "Index": int})

    return fig_projected_wages, fig_real_wages, df_traces_in_projected_wages, df_traces_in_real_wages

# --------------- function for updating figures --------
# triggered when (1) filtered-jobs-data/filtered-names-data stores are updated 
#
# this callback updates figs only by adding/"removing" traces ("not technically removing, just deleting variables")
# also maintains a data frame ledger that tracks what names/jobs currently have traces in the figs
@app.callback(
        ServersideOutput('traces-in-real-wages', 'data'),
        ServersideOutput('traces-in-projected-wages', 'data'),
        Output(ids.PROJECTED_WAGES_LINE_PLOT, "figure"),
        Output(ids.REAL_WAGES_LINE_PLOT, "figure"),
        Output(ids.LOLLIPOP_CHART, "figure"),
        Output('lollipop-chart-title','children'),
        Input(ids.INITIAL_WAGE_INPUT, "value"),
        Input('filtered-combined-data', 'data'),
        Input('refresh-figures-button', 'n_clicks'),
        Input('real-wages-scale-switch', 'value'),
        State(ids.YEAR_RANGE_SLIDER, 'value'),
        State('traces-in-real-wages','data'),
        State('traces-in-projected-wages','data'),
        State(ids.PROJECTED_WAGES_LINE_PLOT, "figure"),
        State(ids.REAL_WAGES_LINE_PLOT, "figure"),
        State(ids.LOLLIPOP_CHART, "figure"),
        State('compensation-type-store', 'data'),
        prevent_initial_call = True,
        blocking = True
)
def update_figures(initial_wage, df_combined_filtered, n_clicks, real_wages_scale_switch_value, years, df_traces_in_real_wages, df_traces_in_projected_wages, fig_projected_wages, fig_real_wages, fig_lollipop, COMPENSATION_TYPE):
    min_year = years[0]
    max_year = years[1]
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if (real_wages_scale_switch_value == True):
        real_wages_axis_type = 'log' # or linear
    else:           # default is linear even
        real_wages_axis_type = 'linear'

    # if just the switch is pushed, only need to update the scale and don't do anything else
    if trigger_id == 'real-wages-scale-switch':
        fig_real_wages['layout']['yaxis']['type']=real_wages_axis_type
        lollipop_chart_title = title="Years: " + str(min_year) + "-" + str(max_year)
        return df_traces_in_real_wages, df_traces_in_projected_wages, fig_projected_wages, fig_real_wages, fig_lollipop, lollipop_chart_title

    # if no names/positions added, df_combined filtered is empty, so just reset plots:
    if len(df_combined_filtered) == 0:
        fig_projected_wages, fig_real_wages, df_traces_in_projected_wages, df_traces_in_real_wages = reset_figures(real_wages_axis_type)
        fig_lollipop = reset_fig_lollipop()
        lollipop_chart_title = title="Years: " + str(min_year) + "-" + str(max_year)
        return df_traces_in_real_wages, df_traces_in_projected_wages, fig_projected_wages, fig_real_wages, fig_lollipop, lollipop_chart_title

    # the innermost if statement should evaluate as true when user moves the year slider or modify input function; if so, resets plots and "ledgers"
    if fig_real_wages is not None:
        if fig_real_wages['layout']['xaxis']['range'] is not None:
            current_fig_min_year = -int(-fig_real_wages['layout']['xaxis']['range'][0]//1)       # this rounds up b/c axes min is less than the smallest year
            current_fig_max_year = int(fig_real_wages['layout']['xaxis']['range'][1]//1)          # this rounds down

            if (current_fig_min_year != min_year) or (current_fig_max_year != max_year) or (trigger_id == ids.INITIAL_WAGE_INPUT):
                fig_projected_wages, fig_real_wages, df_traces_in_projected_wages, df_traces_in_real_wages = reset_figures(real_wages_axis_type)
                fig_lollipop = reset_fig_lollipop()
            else:
                # do not reset real/projected wages figs - build it from dictionaries from their existing state
                fig_real_wages = go.Figure(fig_real_wages)
                fig_projected_wages = go.Figure(fig_projected_wages)
                fig_lollipop = reset_fig_lollipop()

    # the very first invocation of this callback is from updating 'filtered-jobs-data', triggered by the modal closing
    if (df_traces_in_real_wages is None) or (df_traces_in_projected_wages is None) or (trigger_id == 'refresh-figures-button'):
        reset_flag = False
        fig_projected_wages, fig_real_wages, df_traces_in_projected_wages, df_traces_in_real_wages = reset_figures(real_wages_axis_type)
        fig_lollipop = reset_fig_lollipop()

    # for real wages:
    # get names for real_wages figure
    names_wanted_in_real_wages = set(df_combined_filtered.loc[:,DataSchema.NAME])
    names_already_in_real_wages = set(df_traces_in_real_wages.loc[:, DataSchema.NAME])

    # names already in real wages but not in wanted: delete traces
    names_2delete_real_wages = list(names_already_in_real_wages.difference(names_wanted_in_real_wages))
    logical_array = df_traces_in_real_wages[DataSchema.NAME].isin(names_2delete_real_wages)
    indexes_2delete_real_wages = df_traces_in_real_wages.loc[logical_array, 'Index']
    for i in indexes_2delete_real_wages:
        fig_real_wages.data[int(i)]['x'] = []                        # awkward, but can't delete from tuple; can hide/modify inside objects
        fig_real_wages.data[int(i)]['y'] = []  
    
    df_traces_in_real_wages = df_traces_in_real_wages.loc[~logical_array, :]                        # remove deleted traces from the df "ledger"

    # names in wanted but not yet in real wages: add traces
    names_2add_real_wages = list(names_wanted_in_real_wages.difference(names_already_in_real_wages))
    fig_real_wage_indices = list()
    for name in names_2add_real_wages:
        logical_array = df_combined_filtered.loc[:,DataSchema.NAME] == name
        x_var = df_combined_filtered.loc[logical_array,DataSchema.YEAR]
        y_var = df_combined_filtered.loc[logical_array,COMPENSATION_TYPE]

        fig_real_wages.add_trace(go.Scatter(x = x_var, y = y_var, name = name, hovertemplate = '$%{y}'))
        fig_real_wage_indices.append(len(fig_real_wages.data) - 1)     

    df_traces_in_real_wages = pd.concat([df_traces_in_real_wages, pd.DataFrame({DataSchema.NAME: names_2add_real_wages, 'Index': fig_real_wage_indices})]).astype({DataSchema.NAME: "category", "Index": int})     # update ledger

    # for projected wages/lollipop:
    # additional filter for names/jobs that do not span the years
    names_with_min = df_combined_filtered.loc[df_combined_filtered[DataSchema.YEAR] == min_year, DataSchema.NAME]
    names_with_max = df_combined_filtered.loc[df_combined_filtered[DataSchema.YEAR] == max_year, DataSchema.NAME]
    names_wanted_in_projected_wages = set(names_with_max) & set(names_with_min)
    names_already_in_projected_wages = set(df_traces_in_projected_wages.loc[:, DataSchema.NAME])

    # names already in real wages but not in wanted: delete traces
    names_2delete_projected_wages = list(names_already_in_projected_wages.difference(names_wanted_in_projected_wages))
    logical_array = df_traces_in_projected_wages[DataSchema.NAME].isin(names_2delete_projected_wages)
    indexes_2delete_projected_wages = df_traces_in_projected_wages.loc[logical_array, 'Index']
    for i in indexes_2delete_projected_wages:
        fig_projected_wages.data[int(i)]['x'] = []                        # awkward, but can't delete from tuple; can hide/modify inside objects
        fig_projected_wages.data[int(i)]['y'] = []  
    df_traces_in_projected_wages = df_traces_in_projected_wages.loc[~logical_array, :]                        # remove deleted traces from the df "ledger"

    # names in wanted but not yet in real wages: add traces
    names_2add_projected_wages = list(names_wanted_in_projected_wages.difference(names_already_in_projected_wages))
    fig_projected_wage_indices = list()
    for name in names_2add_projected_wages:
        logical_array = df_combined_filtered.loc[:,DataSchema.NAME] == name
        
        pay = df_combined_filtered.loc[logical_array,COMPENSATION_TYPE].to_numpy()
        priorpay = df_combined_filtered.loc[logical_array,COMPENSATION_TYPE].shift(1).to_numpy()
        priorpay[0] = pay[0]
        adjustment = (pay - priorpay)/priorpay + 1
        cumadjustment = pd.Series(adjustment).cumprod() 

        y_var = round(cumadjustment*initial_wage,-2)        # round to 100s to clean up the hover text
        x_var = df_combined_filtered.loc[logical_array,DataSchema.YEAR]
        
        name = 'at ' + name + ' rate'
        fig_projected_wages.add_trace(go.Scatter(x = x_var, y = y_var, hovertemplate = '$%{y}', name=name))
        fig_projected_wage_indices.append(len(fig_projected_wages.data) - 1)     
    

    df_traces_in_projected_wages = pd.concat([df_traces_in_projected_wages, pd.DataFrame({DataSchema.NAME: names_2add_projected_wages, 'Index': fig_projected_wage_indices})]).astype({DataSchema.NAME: "category", "Index": int})     # update ledger
    projected_wages_chart_title = title="Years: " + str(min_year) + "-" + str(max_year)

    # create df_lollipop (pivot_wider the first and last years)
    # df lollipop needs to be reset every time because of sorting by largest to smallest
    df_lollipop = df_combined_filtered[df_combined_filtered[DataSchema.NAME].isin(names_wanted_in_projected_wages)]         # df lollipop uses the same wanted names as projected wages   
    if len(df_lollipop) > 0:
        df_lollipop = df_lollipop.pivot(index=DataSchema.NAME, columns=DataSchema.YEAR, values=COMPENSATION_TYPE).reset_index()

        # sort by ascending wages
        df_lollipop = df_lollipop.sort_values(by=[max_year, min_year], ascending=True)

        lollipop_x_start = df_lollipop[min_year].tolist()
        lollipop_x_end = df_lollipop[max_year].tolist()        
        lollipop_y = df_lollipop[DataSchema.NAME].str.replace(' ','<br>', n=1).tolist()      # also add line break the first space to wrap text

        for i in range(0, len(lollipop_x_start)):
            fig_lollipop.add_trace(go.Scatter(
                        x = [lollipop_x_start[i], lollipop_x_end[i]],
                        y = [lollipop_y[i],lollipop_y[i]],
                        hoverinfo='skip',
                        line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=3)))

        lollipop_marker_size = 9
        fig_lollipop.add_trace(go.Scatter(
                        x=lollipop_x_start,
                        y=lollipop_y,
                        mode = "markers",
                        marker_symbol = "circle",
                        marker_size = lollipop_marker_size,
                        hovertemplate = '$%{x}<br>' + str(min_year) + '<extra></extra>',
                        marker_color=colors.START_MARKER_COLOR,
                    )
        )

        fig_lollipop.add_trace(go.Scatter(
                        x=lollipop_x_end,
                        y=lollipop_y,
                        mode = "markers",
                        marker_size = lollipop_marker_size,
                        hovertemplate = '$%{x}<br>' + str(max_year) + '<extra></extra>',
                        marker_color=colors.END_MARKER_COLOR)
        )

        lollipop_chart_title = title="Years: " + str(min_year) + "-" + str(max_year)
        #fig_lollipop.layout.template.layout.height = (len(lollipop_y)-5)*100+400
        if len(lollipop_y) < 6:
            fig_lollipop.update_layout(height = 400)
        else:
            fig_lollipop.update_layout(height = (len(lollipop_y)-6)*50+400)            # increase height by 30px for each additional person past 5
    return df_traces_in_real_wages, df_traces_in_projected_wages, fig_projected_wages, fig_real_wages, fig_lollipop, lollipop_chart_title

# run script
if __name__ == '__main__':
     app.run_server(debug=True)