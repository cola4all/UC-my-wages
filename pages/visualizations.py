#from dash import callback_context as ctx
from dash.exceptions import PreventUpdate
from dash import  Output, Input, State, html, dcc, dash_table, page_container, page_registry, register_page, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os, pathlib
import time
import numpy as np


register_page(__name__, path="/")

APP_PATH = os.path.split(str(pathlib.Path(__file__).parent.resolve()))[0]       # the 0th element of os path split moves back one subfolder
PROPOSAL_DATA_PATH = os.path.join(APP_PATH, "assets", "wage_proposals.csv")
UNIVERSITIES_DATA_PATH = os.path.join(APP_PATH, "assets", "wage_by_university.csv")
LIVING_WAGE_DATA_PATH = os.path.join(APP_PATH, "assets", "living_wage_by_university.csv")
IMAGE_PATH = os.path.join("..","assets","union_other_contracts_graphic.png")

class colors:
    PLOT_BACKGROUND_COLOR = "#edeff1"
    END_MARKER_COLOR = "#355218"
    START_MARKER_COLOR = "#759356"
    LOLLIPOP_LINE_COLOR = "#7B7B7B"
    GRID_LINES_COLOR = "#C5CCCA"

##### create universities comparison plot layout
t0 = time.time()
print('reading csv 3:')
df_universities = pd.read_csv(UNIVERSITIES_DATA_PATH)
df_living_wage = pd.read_csv(LIVING_WAGE_DATA_PATH)
UC_list = ["UC Merced", "UC Riverside", "UC Davis", "UC Los<br>Angeles<br>", "UC San Diego", "UC Berkeley", "UC Irvine", "UC Santa<br>Barbara<br>", "UC Santa<br>Cruz<br>", "UC San<br>Francisco<br>"]
UC_list.reverse()
print(time.time() - t0)

def reset_fig_universities():
    fig_universities = go.Figure()

    universities_template = go.layout.Template()
    universities_template.layout = go.Layout(
        paper_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        showlegend=False,
        title_font=dict(family="Arial", size=20),
        title_x=0,
        yaxis=dict(linewidth=1, linecolor = "black", 
            showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
            automargin =True,
            showline = False,
            fixedrange = True,
            ticklabelposition="inside top",
            ticklabeloverflow = "allow",
        ),
        xaxis=dict(zeroline = False, rangemode = "tozero",
            title = dict(text = "Monthly Wage (USD)"),
            showgrid=True,  gridcolor = colors.GRID_LINES_COLOR, gridwidth=1,
            showline = True, linewidth=1, linecolor = "black",
            fixedrange = True, automargin = True,
            title_standoff = 15
        ),
        margin = dict(autoexpand = True, r=0, t=0, b=40, l=10),
        dragmode = False,   
    )

    fig_universities.update_layout(template=universities_template)
    fig_universities.update_xaxes(showspikes=True, spikecolor="gray", spikemode="across", spikethickness=2)

    return fig_universities

fig_universities = reset_fig_universities()

universities_comparison_div = html.Div(
    [
        html.H4('How does our tentative agreement compare to other grad worker union contracts?'),
        dbc.Row([
            dbc.Col(
                [
                    dbc.Row([
                        dbc.Col(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            [
                                                dbc.RadioItems(
                                                    options=[
                                                        {"label": "GSR", "value": 1, "label_id": "GSR-label"},
                                                        {"label": "ASE", "value": 2, "label_id": "ASE-label"},
                                                    ],
                                                    id="position-radio-items",
                                                    className="btn-group",
                                                    inputClassName="btn-check",
                                                    labelClassName="btn btn-outline-primary",
                                                    labelCheckedClassName="active",
                                                    value=1,
                                                    inline=True,
                                                ), 
                                            ],
                                            className="radio-group",
                                        ), 
                                        align="center",
                                        width="auto"
                                    ),
                                    dbc.Col(html.Span(html.I(className="bi bi-info-circle", style={"color":"black", "font-size":"1rem"}), id="GSR-ASE-info"), width="auto", align="center", style={"margin-right":"auto", "padding": "0"}),         
                                ]
                            ),
                            md="auto", sm=5, xs=12,
                        ),
                        dbc.Popover(
                            [
                                dbc.PopoverBody("GSR = Graduate Student Researchers\nASE = Academic Student Employees"),
                            ],
                            target="GSR-ASE-info", placement="bottom", trigger="legacy"
                        ),
                        dbc.Col(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            [
                                                dbc.RadioItems(
                                                    options=[
                                                        {"label": "Wage", "value": 1},
                                                        {"label": "Wage-to-Living Wage", "value": 2},
                                                    ],
                                                    id="wage-type-radio-items",
                                                    className="btn-group",
                                                    inputClassName="btn-check",
                                                    labelClassName="btn btn-outline-primary text-nowrap",
                                                    labelCheckedClassName="active",
                                                    value=2,
                                                    inline=True,
                                                ), 
                                            ],
                                            className="radio-group",
                                        ), 
                                        align="center",
                                        width="auto"
                                    ),
                                    dbc.Col(html.Span(html.I(className="bi bi-info-circle", style={"color":"black", "font-size":"1rem"}), id="wages-type-info"), width="auto", align="center", style={"margin-right":"auto", "padding": "0"}),
                                ]
                            ),
                            md="auto", sm=7, xs=12,
                        ),
                        dbc.Popover(
                            [
                                dbc.PopoverBody("The Wage option plots the actual wage based on published pay scale charts.", style={"padding-bottom":".25rem"}),
                                dbc.PopoverBody("The Wage-to-Living Wage option plots the actual wage divided by the local (county-level) living wage obtained from MIT Living Wage Calculator.", style={"padding-top":".25rem"})
                            ],
                            target="wages-type-info", placement="bottom", trigger="legacy"
                        ),
                        dbc.Col(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            [
                                                dbc.RadioItems(
                                                    options=[
                                                        {"label": "Apr 2023", "value": 1},
                                                        {"label": "Oct 2023", "value": 2},
                                                        {"label": "Oct 2024", "value": 3},
                                                    ],
                                                    id="date-radio-items",
                                                    className="btn-group",
                                                    inputClassName="btn-check",
                                                    labelClassName="btn btn-outline-primary text-nowrap",
                                                    labelCheckedClassName="active",
                                                    value=1,
                                                    inline=True,
                                                ), 
                                            ],
                                            className="radio-group",
                                        ), 
                                        align="center",
                                        width="auto"
                                    ),
                                    dbc.Col(html.Span(html.I(className="bi bi-info-circle", style={"color":"black", "font-size":"1rem"}), id="date-info"), width="auto", align="center", style={"margin-right":"auto", "padding": "0"}),
                                ]
                            ),
                            md="auto", sm=12, xs=12,
                        ),
                        dbc.Popover(
                            [
                                dbc.PopoverBody("These 3 dates correspond to when each raise would take effect, according to the tentative agreement."),
                            ],
                            target="date-info", placement="bottom", trigger="legacy"
                        ),
                    ],
                    style = {"justify-content": "space-between", "padding-right": "1rem"}
                    ),
                    html.P(),
                    dcc.Graph(figure=fig_universities, config={'displayModeBar': False}, id='fig-universities')
                ],
                xl=9,lg=12
            ),
            dbc.Col(
                [
                    html.P(),
                    html.H5("How to use this chart:"),
                    dcc.Markdown("Each data point corresponds to the base wage for each step in the university's pay scale. Hover over each data point to view details. In our view, the most informative data point to compare across campuses is the **minimum monthly wage (the largest data points)**."),
                    dcc.Markdown("*Some but not all* of the base pays at higher pay scales are also plotted (the smaller data points). The policy for classifying grad workers at higher pay scales varies across universities, and departments often pay more than the contractually obligated minimum base wage. As such, it is difficult to draw general conclusions by comparing the base pay at higher pay scales across universities."),
                ], 
                class_name="align-self-end"
            )
        ],
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Why did we build this chart?"),
                        dcc.Markdown("The Union has touted the gains in the tentative agreement as *historic*, citing the relative % wage increase compared to othe grad unions (see image)."),
                        dcc.Markdown("However, what matters to grad workers is **not** relative % wage increase, but the real monthly wage and how it relates to local housing costs. **The Wage-to-Living Wage** chart aims to visualize how far our actual wages are from a living wage. The green dashed line denotes the point at which Actual Wage matches Living Wage."),
                        dcc.Markdown("While this tentative agreement brings some UC grad workers closer to parity with our peers at other universities, we would need to wait 2.5 years, and a substantial portion of our Union membership would still experience extreme rent burden."),
                    ],
                    md=8,sm=12
                ),
                dbc.Col(
                    [
                        dbc.Row(html.Img(src=IMAGE_PATH, style={"width":"100%"})),
                        dbc.Row(dcc.Markdown("[UAW Graphic](https://www.fairucnow.org/ta-summary/) comparing the % wage increase of union contracts at peer institutions.", style={"font-size":"0.9rem"}))
                    ]
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Data Source and Limitations"),
                        dcc.Markdown("The Actual Wage to Living Wage ratio roughly approximates monthly wages accounting for cost of living based on locality. We divided the actual monthly wage by the living wage of the county that the school is located in, as determined by the [MIT Living Wage Calculator](https://livingwage.mit.edu/). To project Living Wage for Oct 2023 and Oct 2024, we assumed a conservative 2% increase in living expenses for each year."),
                        dcc.Markdown("One caveat is that the Living Wage is a county-wide measure, and the size of the counties vary greatly between schools. For example, the Living Wage for UCLA includes all of LA County, whereas the Living Wage for Columbia only includes New York County (which is just Manhattan). A more localized measure of cost of living (e.g., median rent in the immediate neighborhood) would be more accurate but would take more time to collate."),
                        dcc.Markdown("The data sources comes from official HR documents or union contracts: [UC ASE tentative agreement](https://docs.google.com/spreadsheets/d/1yw3tehPnOz6girjThLt7CTJAqyLOA8LF/edit#gid=897821721), [UC GSR tentative agreement](https://drive.google.com/file/d/1yslPwqC9rBKao2flYmEdSM7pRAXCb-Ib/view), [Harvard contract](https://harvardgradunion.org/wp-content/uploads/2022/02/Clean-version-of-new-CBA-no-red-lines-1-25-22.pdf), [Columbia minimum pay](https://studentbenefits.provost.columbia.edu/content/compensation-and-student-employee-benefits), and [University of Washington contract](https://hr.uw.edu/labor/academic-and-student-unions/uaw-ase/ase-contract)")
                    ],
                    width=12
                ),
            ]
        )
    ]
)

## Include sources:
# HUD small area fair market rent: https://www.huduser.gov/portal/datasets/fmr/fmrs/FY2023_code/select_Geography_sa.odn
# HUD fair market rent: https://www.huduser.gov/portal/datasets/fmr.html

##### create proposal plot
t0 = time.time()
print('reading csv 4:')
df_proposal = pd.read_csv(PROPOSAL_DATA_PATH)
print(time.time() - t0)


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
        title = dict(text = "12-Month Base Pay (USD)"),
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

proposal_marker_size = 6
                
for i in range(0, len(proposal_x_sru_nov30)):         
    fig_proposal.add_trace(go.Scatter(
                showlegend=False,
                mode = "lines",
                x = [proposal_x_sru_dec8[i], proposal_x_sru_nov14[i]],
                y = [proposal_y[i],proposal_y[i]],
                hoverinfo='skip',
                line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=2, dash='dot')))

for i in range(0, len(proposal_x_sru_dec8)):             # this skips the last two missing from uaw
    fig_proposal.add_trace(go.Scatter(
                showlegend=False,
                mode = "lines",
                x = [proposal_x_uc_dec15[i], proposal_x_sru_dec8[i]],
                y = [proposal_y[i],proposal_y[i]],
                hoverinfo='skip',
                line=dict(color=colors.LOLLIPOP_LINE_COLOR, width=2)))

for i in range(0, len(proposal_x_current)):         
    fig_proposal.add_trace(go.Scatter(
                showlegend=False,
                mode = "lines",
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


wage_proposal_div = html.Div(
    [
        html.H4('How have the UAW and UC base pay proposals changed over the course of negotiations?'),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_proposal, config={'displayModeBar': False}),xl=9,lg=12),
            dbc.Col([
                html.P(),
                html.P("These base pays would be effective starting Oct 2023 and assume a 12-month appointment (although a 12-month appt is not guaranteed for ASE's)."),
                html.P("Current data reflects proposals from Dec 8 (UAW) and Dec 15 (UC). We will be updating the tracker as proposed wages are verified."),
                dcc.Markdown("This plot aims to visualize the movement on a central bargaining issue over the course of negotiations between the two bargaining parties."),
                dcc.Markdown("As a disclaimer, the data used in the visualization summarizes base wage proposals using information that is most generalizable across all grad workers. The visualization does not reflect details like campus-based adjustments and new experience-based increments. For complete proposal details, please see the bargaining update documents from [FairUCNow](https://www.fairucnow.org/bargaining/)."),
            ], class_name="align-self-end")
        ],
        )
    ]
)

layout = html.Div(
    [
        dcc.Interval(id='page-load-interval', n_intervals=0, max_intervals=0, interval=1), # max_intervals = 0 ensures callback only runs once at startup
        universities_comparison_div,
        html.Hr(),
        wage_proposal_div,
    ],
    className="content-div"
)


##### create university wage comparison plot

@callback(
    Output('fig-universities', 'figure'),
    Input('position-radio-items', 'value'),
    Input('wage-type-radio-items', 'value'),
    Input('date-radio-items', 'value'),
    prevent_initial_call = False
)
def update_fig_universities(radio_value, wage_value, date_value):   
    fig_universities = reset_fig_universities()

    if radio_value==1:
        position = "GSR"
    elif radio_value==2:
        position = "ASE"

    if wage_value==1:
        wage = "Wage"
    elif wage_value==2:
        fig_universities.add_vline(x=1,line_width=2, line_dash="dash", line_color="#4D7E40")
        wage = "Wage-to-Rent"

    if date_value==1:
        date = "Apr 2023"
    elif date_value==2:
        date = "Oct 2023"
    elif date_value==3:
        date = "Oct 2024"

    WAGE_COLUMN = date + " (monthly)"
    LIVING_WAGE_COLUMN = date + " (living monthly wage)"

    dff_universities = df_universities[df_universities['Position']==position]

    unique_schools = dff_universities['School'].unique().tolist()
    if wage_value == 2:
        if position == "ASE":
            unique_schools = unique_schools[:-2]
            unique_schools.extend(UC_list)
        elif position == "GSR":
            unique_schools = unique_schools[:-1]
            unique_schools.extend(UC_list)

    for school in unique_schools:

        # determine which logical array to use
        if wage_value == 1:
            living_wage_adj = 1
            logical_array = dff_universities['School']==school
            hovertemplate = '%{customdata[0]}<br>$%{x:,.2f}<extra></extra>'
        elif wage_value == 2:
            living_wage_adj = df_living_wage.loc[df_living_wage['School']==school,LIVING_WAGE_COLUMN].iloc[0]
            hovertemplate = '%{customdata[0]}<br>%{x:,.2f}<extra></extra>'
            if "UC " in school:
                if position == "ASE":
                    if df_living_wage.loc[df_living_wage['School']==school,'Tier'].iloc[0] == 1:
                        logical_array = dff_universities['School']=="UC Tentative<br>Agreement<br>(Tier 1 Campus)<br><br>"
                    elif df_living_wage.loc[df_living_wage['School']==school, 'Tier'].iloc[0] == 2:
                        logical_array = dff_universities['School']=="UC Tentative<br>Agreement<br>(Tier 2 Campus)<br><br>"
                elif position == "GSR":
                    logical_array = dff_universities['School']=="UC Tentative<br>Agreement<br>"
            else:
                logical_array = dff_universities['School']==school      
        

        if sum(logical_array) > 1:          # only plot line if more than 1 data point available
            fig_universities.add_trace(go.Scatter(
                        showlegend=False,
                        mode = "lines",
                        x = dff_universities.loc[logical_array, WAGE_COLUMN]/living_wage_adj,
                        y = [school]*sum(logical_array),
                        hoverinfo='skip',
                        line=dict(color = dff_universities.loc[logical_array,"Line Color"].iloc[0], width=2)))

        minimum_logical_array = logical_array & (dff_universities['Minimum'] == 1)
        customdata = np.stack((dff_universities.loc[minimum_logical_array,'Step'], dff_universities.loc[minimum_logical_array,'Position']), axis=-1)
        fig_universities.add_trace(go.Scatter(
                    showlegend=False,
                    mode = "markers",
                    marker_symbol = "circle",
                    x = dff_universities.loc[minimum_logical_array , WAGE_COLUMN]/living_wage_adj,
                    y = [school]*sum(minimum_logical_array),
                    customdata=customdata,                
                    hovertemplate = hovertemplate,
                    marker=dict(color = dff_universities.loc[minimum_logical_array ,"Marker Color"].iloc[0],size=10)))

        non_minimum_logical_array = logical_array & (dff_universities['Minimum'] == 0)
        customdata = np.stack((dff_universities.loc[non_minimum_logical_array,'Step'], dff_universities.loc[non_minimum_logical_array,'Position']), axis=-1)
        if sum(non_minimum_logical_array) > 0:          # only plot line if more than 0 data point available
            fig_universities.add_trace(go.Scatter(
                        showlegend=False,
                        mode = "markers",
                        marker_symbol = "circle",
                        x = dff_universities.loc[non_minimum_logical_array , WAGE_COLUMN]/living_wage_adj,
                        y = [school]*sum(non_minimum_logical_array),
                        customdata=customdata,                
                        hovertemplate = hovertemplate,
                        marker=dict(color = dff_universities.loc[non_minimum_logical_array ,"Marker Color"].iloc[0],size=6, opacity=.5)))

    # fix the range of the x axes depending on the type of wages used
    if wage_value == 1:
        fig_universities.update_xaxes(range=[0,5000], title = dict(text = "Monthly Wage (USD)"))
    elif wage_value == 2:
        fig_universities.update_xaxes(range=[0,1.55], title = dict(text = "Actual Wage to Living Wage"))

    # dynamically adjust height of plot
    if len(unique_schools) < 6:
        fig_universities.update_layout(height = 400)
    else:
        fig_universities.update_layout(height = (len(unique_schools)-6)*50+400)            # increase height by 30px for each additional person past 5    

    return fig_universities


