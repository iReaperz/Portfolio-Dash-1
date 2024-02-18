import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
from dash import  dcc, html, Input, Output, callback


dash.register_page(__name__, path='/waterfall', name="Waterfall Plot")


# Define a function to calculate 'pchg' and 'MaxPchg' for each group
def calculate_pchg(group):
    group['pchg'] = 100 * (group['aval'] - group['base']) / group['base']
    group['MaxPchg'] = group['pchg'].max()
    return group

adlbc_raw = pd.read_csv(("raw/adlbc.csv"))

layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Header("Parameter Category:", style={'color' : "#17c6d3"}),
            dcc.Dropdown(id = "mydropdown", options = [value for value in adlbc_raw["paramcd"].unique() if not value.startswith('_')],
                                                       value = "GGT", style={'margin-top' : "15px"}
            ),
            html.Div([
                html.Footer("Follow us:", style={'color': "#17c6d3", 'display': 'inline-block', 'vertical-align': 'middle'}),
                html.A(
                    html.Img(src="assets/linked.png", className="linked-img"),
                    href="link1",
                    style={'display': 'inline-block'}
                ),
                html.A(
                    html.Img(src="assets/git.png", className="git-img"),
                    href="link2",
                    style={'display': 'inline-block'}
                ),
                html.A(
                    html.Img(src="assets/medium.png", className="medium-img"),
                    href="link3",
                    style={'display': 'inline-block'}
                )
            ], className="plotWB"),
        ], className = "dropDownBW"),
        html.Div([
            dcc.Graph(id = "waterfall", className="graph-class")
        ], className = "graph-div")
    ], className="main-div"),
], className="container")


                                                                             
def create_waterfall_plot(trt_selection):
    filtered_data = adlbc_raw[(adlbc_raw['paramcd'] == trt_selection) & (adlbc_raw['saffl'] == "Y") & (adlbc_raw['avisitn'] > 0)]
    grouped_data = filtered_data.groupby(['trta', 'usubjid']).apply(calculate_pchg)

    # Remove the grouping and flatten the multi-level index
    grouped_data = grouped_data.reset_index(drop=True).groupby("usubjid").head(1).dropna(subset=['pchg'])
    grouped_data = grouped_data.reset_index()[["trta", "usubjid", "MaxPchg"]]
    grouped_data['MaxPchg'] = np.where(grouped_data['MaxPchg'] > 100, 100, grouped_data['MaxPchg'])
    grouped_data['xValues'] = grouped_data.groupby('trta').cumcount() + 1
    
    sorted_data = grouped_data.sort_values(by='MaxPchg', ascending=False)
    sorted_data['xValues_sorted'] = range(1, len(sorted_data) + 1)

    
    master_fig = make_subplots(rows=len(grouped_data["trta"].unique()), cols=1, subplot_titles=grouped_data["trta"].unique(), vertical_spacing=0.065)
    for i, trt in enumerate(grouped_data["trta"].unique()):
        sorted_data = grouped_data[grouped_data["trta"] == trt].sort_values(by='MaxPchg', ascending=False)
        sorted_data['xValues_sorted'] = range(1, len(sorted_data) + 1)

        list_x = list(sorted_data['xValues_sorted'][sorted_data["MaxPchg"] == 100])

        # Add traces
        trace = go.Bar(x=sorted_data['xValues_sorted'], y=sorted_data['MaxPchg'], text=["U" for x in list_x],
                    textposition='outside', insidetextanchor='start',
                    hovertemplate='<b>Subject</b>: %{customdata}<br>' +
                                    '<b>X Value</b>: %{x}<br>' +
                                    '<b>Change</b>: %{y}' +
                                    '<extra></extra>',
                    customdata=sorted_data["usubjid"])

        rect_shape = go.layout.Shape(
            type='rect', xref='x', yref='y',
            x0=0, y0=sorted_data['MaxPchg'].min() - 10, x1=len(sorted_data) + 1, y1=sorted_data['MaxPchg'].max() + 12,
            line={'width': 1, 'color': 'black'}
        )

        master_fig.add_trace(trace, row=i + 1, col=1)
        master_fig.add_shape(rect_shape, row=i + 1, col=1)

        # Update y-axis range
        master_fig.update_yaxes(range=[sorted_data['MaxPchg'].min() - 10, sorted_data['MaxPchg'].max() + 12], row=i + 1, col=1)

    # Update subtitles
    for i, trt in enumerate(grouped_data["trta"].unique()):
        master_fig['layout']['annotations'][i].update(text=f'{trt}')

    # Add text with increased margin
    master_fig.update_layout(height=1300, title_text=f"<b>Waterfall Plot of Maximum Post Baseline Percentage Change in {trt_selection}</b>",title_x=0.5,showlegend=False,
                            plot_bgcolor='white', margin=dict(b=100), title_font=dict(size=24, family="Balto")  # Increase the bottom margin
    )

    master_fig.add_annotation(showarrow=False,xref='paper', x=-0.05, yref='paper',y=0.5,textangle=-90,text="Maximum post baseline percentage change",font=dict(size=14.5))
    master_fig.add_annotation(text="Each bar represents unique subject's maximum percentage change.", x=0, y=-0.05, showarrow=False, xref="paper", yref="paper",font=dict(size=12))
    master_fig.add_annotation(text="If subject's maximum percentage change was greater than 100 percent then the change was displayed as 100 and indicated with the letter U in plot.", 
                            x=0, y=-0.07, showarrow=False, xref="paper", yref="paper",font=dict(size=12))

    return master_fig   

@callback(Output("waterfall", "figure"),
              Input("mydropdown", "value"))
def sync_input(trt_selection):
    return create_waterfall_plot(trt_selection)
