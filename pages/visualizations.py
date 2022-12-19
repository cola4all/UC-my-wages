#from dash import callback_context as ctx
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc, dash_table, ServersideOutput, ServersideOutputTransform, MultiplexerTransform, register_page, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os, pathlib
import time

import dash

register_page(__name__, path="/")

APP_PATH = os.path.split(str(pathlib.Path(__file__).parent.resolve()))[0]       # the 0th element of os path split moves back one subfolder
PROPOSAL_DATA_PATH = os.path.join(APP_PATH, "assets", "wage_proposals.csv")

class colors:
    PLOT_BACKGROUND_COLOR = "#edeff1"
    END_MARKER_COLOR = "#355218"
    START_MARKER_COLOR = "#759356"
    LOLLIPOP_LINE_COLOR = "#7B7B7B"
    GRID_LINES_COLOR = "#C5CCCA"


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

layout = html.Div([
    html.H4('UAW vs UC Base Pay Proposals'),
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
],
className="content-div"
)