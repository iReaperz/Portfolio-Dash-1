import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import  dcc, html, Input, Output, callback

dash.register_page(__name__, path='/scatterplot', name="Scatter Plot")

#Importing data
adlbc_raw = pd.read_csv("raw/adlbc.csv")
adsl_raw = pd.read_csv("raw/adsl.csv")
adsl_raw.rename(columns={'trt01a': 'trta'}, inplace=True)

layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Header("Parameter Category 1:", style={'color': "#17c6d3"}),
            dcc.Dropdown(
                id="first_paramcd",
                options=[{'label': value, 'value': value} for value in adlbc_raw["paramcd"].unique() if not value.startswith('_')],
                value="BILI",
                style={'margin-top': "5px"}
            ),
            html.Header("Parameter Category 2:", style={'margin-top': "20px", 'color': "#17c6d3"}),
            dcc.Dropdown(
                id="second_paramcd",
                options=[{'label': value, 'value': value} for value in adlbc_raw["paramcd"].unique() if not value.startswith('_')],
                value="ALT",
                style={'margin-top': "5px"}
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
            ], className="plotSC"),
        ], className="dropDownSC"),
        html.Div([
            dcc.Graph(id="scatterplot", className="graph-class")
        ], className = "graph-div")
    ], className="main-div"),
], className="container")




def create_scatter_plot(first_val, second_val):
    if first_val == second_val:
        return {
            'data': [],
            'layout': {
                'annotations': [{'text': 'Please choose different values for the two dropdowns.', 'showarrow': False, 'x': 2.5, 'y': 2.5, 'font': {'size': 16,}}],
                'xaxis': {'showline': False,'showgrid': False,'zeroline': False,'showticklabels': False,'title': ''},
                'yaxis': {'showline': False,'showgrid': False,'zeroline': False,'showticklabels': False,'title': ''}
            }
        }

    # Filtering data
    adlbc = adlbc_raw[(adlbc_raw['avisitn'] > 0) & (adlbc_raw['saffl'] == 'Y') & (adlbc_raw['paramcd'].isin([first_val, second_val]))]
    # Calculating number of subjects in each treatment group
    N_Subjs = adsl_raw.groupby('trta').size().reset_index(name='Count')

    # Calculating reference lines
    highs_lows = adlbc.sort_values('paramcd').groupby('paramcd').agg({'a1hi': 'min', 'a1lo': 'max'}).reset_index()
    RefLineH1, RefLineH2 = highs_lows['a1hi'].values
    RefLineL1, RefLineL2 = highs_lows['a1lo'].values

    # Calculating maximum results
    MaxRslts1 = adlbc.dropna(subset=['aval']).groupby(['paramcd', 'trta', 'usubjid'],).agg({'aval': 'max'}).reset_index()
    # Merging with the number of subjects
    MaxRslts2 = pd.merge(MaxRslts1, N_Subjs, on = "trta", how='left')
    MaxRslts2['N_trt'] = MaxRslts2['trta'] + "(N=" + MaxRslts2['Count'].astype(str) + ")"
    transposed = MaxRslts2.pivot(index=["usubjid","trta","N_trt"], columns='paramcd', values='aval')
    n_levels = transposed.index.get_level_values('N_trt')

    fig = px.scatter(transposed, x=second_val, y=first_val, facet_col=n_levels, color=n_levels, 
                 facet_col_spacing = 0.001)

    fig.add_hline(y=RefLineH2,line_width=2, line_dash="dash", line_color="gray")
    fig.add_hline(y=RefLineL2,line_width=2, line_dash="dash", line_color="gray")
    fig.add_vline(x=RefLineH1,line_width=2, line_dash="dash", line_color="gray")
    fig.add_vline(x=RefLineL1,line_width=2, line_dash="dash", line_color="gray")

    for i,anno in enumerate(fig['layout']['annotations']):
        anno['text']=[f"{col_name}" for col_name in n_levels.unique()][i]

    fig.update_traces(mode="markers", 
                    hovertemplate= '<b>Subject</b>: %{customdata}<br>' +
                                    f'<b>{second_val}</b>: %{{x}}<br>' +
                                    f'<b>{first_val}</b>: %{{y}}'+
                                    '<extra></extra>',
                    customdata=transposed.index.get_level_values('usubjid').unique())


    fig.update_xaxes(title_text='',ticks='inside',linecolor='black',type="log",mirror=True)
    fig.update_yaxes(title_text='',ticks='inside',linecolor='black',type="log",mirror=True)

    fig.add_annotation(showarrow=False,xref='paper', x=0.5, yref='paper',y=-0.06,text=f'Maximum post baseline {second_val}', font=dict(size=14))
    fig.add_annotation(showarrow=False,xref='paper', x=-0.06, yref='paper',y=0.5,textangle=-90,text=f'Maximum post baseline {first_val}',font=dict(size=14))
    fig.add_annotation(showarrow=False,xref='paper', x=0, yref='paper',y=-0.07,text='Each data point represents a unique subject.')
    fig.add_annotation(showarrow=False,xref='paper', x=0, yref='paper',y=-0.09,text='Logarithmic scaling was used on both X and Y axis.')

    fig.update_layout(plot_bgcolor='white',showlegend=False, title_text=f'<b>Scatter Plot of {first_val} vs {second_val} (Safety Analysis Set)</b>', title_x=0.5, title_font=dict(size=24, family="Balto"))

    return fig


@callback(Output("scatterplot", "figure"),
              [Input("first_paramcd", "value"),
               Input("second_paramcd", "value")])
def update_scatter_plot(first_val, second_val):
    return create_scatter_plot(first_val, second_val)
