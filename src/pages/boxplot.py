import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import  dcc, html, Input, Output, callback
import warnings

# Ignore all future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

dash.register_page(__name__, path='/boxplot', name="Box Plot")

adlbc_raw = pd.read_csv("raw/adlbc.csv")

def create_box_plot(trt_selection):
    adlbc_filtred = adlbc_raw[(adlbc_raw["paramcd"] == trt_selection) & (adlbc_raw["avisitn"].notnull())]          
    adlbc_plot = adlbc_filtred[["aval","avisitn","trta"]].sort_values(by="avisitn").astype({"avisitn":"str"})

    fig = px.box(adlbc_plot, x = "avisitn", y = "aval", color = "trta")

    fig.update_layout(xaxis_title = "Visit", yaxis_title = f"Analysis value: {trt_selection.title()}", template = "simple_white",
                      legend = dict(orientation = "h", 
                                    title = "", x = 0.3, y = -0.1,
                                    font = dict(size = 12, color = "black"), bordercolor = "black", borderwidth = 1), 
                      title_text="<b>Test Results for {} in Each Visit<b>".format(trt_selection.title()), title_x=0.5, title_font=dict(size=24, family="Balto"))
    
    fig.update_traces(hovertemplate= f'<b>{trt_selection}/b>: %{{y}}<br>' +
                                     '<b>Visit Number</b>: %{x}')
    
    return fig

layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Header("Parameter Category:", style={'color': "#17c6d3"}),
            dcc.Dropdown(
                id="mydropdown", 
                options=[{'label': value, 'value': value} for value in adlbc_raw["paramcd"].unique() if not value.startswith('_')],
                value="SODIUM",
                style={'margin-top': "15px"}
            ),
            html.Div([
                html.Footer("Follow me:", style={'color': "#17c6d3", 'display': 'inline-block', 'vertical-align': 'middle'}),
                html.A(
                    html.Img(src="assets/linked.png", className="linked-img"),
                    href="https://www.linkedin.com/in/noy-simonyan-888683266/",
                    style={'display': 'inline-block'}
                ),
                html.A(
                    html.Img(src="assets/git.png", className="git-img"),
                    href="https://github.com/iReaperz",
                    style={'display': 'inline-block'}
                )
            ], className="plotWB"),
        ], className="dropDownBW"),
        html.Div([
            dcc.Graph(id="boxPlot", className="graph-class")
        ], className = "graph-div")
    ], className="main-div"),
], className="container")


@callback(Output("boxPlot", "figure"),
              Input("mydropdown", "value"))
def update_box_plot(trt_selection):
    return create_box_plot(trt_selection)