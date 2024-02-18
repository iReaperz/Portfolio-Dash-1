import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import  dcc, html, Input, Output, callback


dash.register_page(__name__, path='/', name="Series Plot")

raw = pd.read_csv("raw/adlbc.csv")

layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Header("Subject ID:", style={'color' : "#17c6d3"}),
            dcc.Dropdown(
                id="usubjid",
                options=[{'label': value, 'value': value} for value in raw["usubjid"].unique() if not value.startswith('_')],
                value="01-701-1015", style={'margin-top' : "5px"}
            ),
            html.Header("Parameter Category 1:", style={'margin-top' : "20px", 'color' : "#17c6d3"}),
            dcc.Dropdown(
                id="first_paramcd",
                options=[{'label': value, 'value': value} for value in raw["paramcd"].unique() if not value.startswith('_')],
                value="ALT", style={'margin-top' : "5px"}
            ),
            html.Header("Parameter Category 2:", style={'margin-top' : "20px", 'color' : "#17c6d3"}),
            dcc.Dropdown(
                id="second_paramcd",
                options=[{'label': value, 'value': value} for value in raw["paramcd"].unique() if not value.startswith('_')],
                value="AST", style={'margin-top' : "5px"}
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
            ], className="plotSE"),
        ], className = "dropDownSE"),
        html.Div([
            dcc.Graph(id="seriesplot", className="graph-class")
        ], className = "graph-div")
    ], className="main-div"),
], className="container")


def create_series_plot(subjid, first_val, second_val):
    if first_val == second_val:
        return {
            'data': [],
            'layout': {
                'annotations': [{'text': 'Please choose different values for the two dropdowns.', 'showarrow': False, 'x': 2.5, 'y': 2.5, 'font': {'size': 16,}}],
                'xaxis': {'showline': False,'showgrid': False,'zeroline': False,'showticklabels': False,'title': ''},
                'yaxis': {'showline': False,'showgrid': False,'zeroline': False,'showticklabels': False,'title': ''}
            }
        }

    filtered_raw = raw[(raw["paramcd"].isin([first_val, second_val])) & 
                       (raw["avisitn"] >= 0) & (raw["saffl"] == "Y")]

    # Preparing data for further analysis
    uln_values = filtered_raw.groupby("paramcd").agg(minUALN=("a1hi", "min"), maxUALN=("a1hi", "max")).reset_index()
    alt_min = uln_values.loc[uln_values["paramcd"] == first_val, "minUALN"].values[0]
    ast_min = uln_values.loc[uln_values["paramcd"] == second_val, "minUALN"].values[0]

    filtered_raw = filtered_raw[filtered_raw["usubjid"] == subjid]
    table_data = filtered_raw.groupby(["paramcd", "ady"]).sum("chg").reset_index().pivot(index="paramcd", columns="ady", values="chg")
    colors = ["purple", "darkgreen"]
    line_types = ["dash", "longdash"]

    fig = go.Figure()
    for i, paramcd in enumerate(filtered_raw["paramcd"].unique()):
        fig.add_trace(go.Scatter(
            x=filtered_raw["ady"][filtered_raw["paramcd"] == paramcd].astype({"ady":"str"}),
            y=filtered_raw["aval"][filtered_raw["paramcd"] == paramcd],
            marker=dict(color=colors[i]),
            line=dict(dash = line_types[i]),
            name=paramcd
        ))


    fig.add_hline(y=alt_min,line_width=1, line_dash="solid", line_color="gray", opacity=0.7)
    fig.add_hline(y=ast_min,line_width=1, line_dash="solid", line_color="gray", opacity=0.7)

    fig.update_layout(height =800, template = "simple_white",
                        legend = dict(orientation = "h", 
                                    title = "", x = 0.5, y = 0.155,
                                    font = dict(size = 12, color = "black"), bordercolor = "black", borderwidth = 1), 
                        title_text=f"<b>{first_val} and {second_val} Results Over Time. (Safety Analysis Set)</b>", title_x=0.535,
                        title_font=dict(size=24, family="Balto"))

    fig.add_trace(go.Table(
        header=dict(values=[], fill=dict(color='rgba(0, 0, 0, 0)')),
        cells=dict(
            values=[table_data[param].round(3) for param in table_data.columns],
            fill=dict(color='rgba(0, 0, 0, 0)')
        ),
        domain=dict(y=[0, 0.1])  # Adjust the y values as needed
    ))

    # Adjust the yaxis domain to leave space for the table
    fig.update_layout(
        yaxis=dict(domain=[0.25, 1])  # Adjust the values as needed
    )

        
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[str(val) for val in filtered_raw["ady"][filtered_raw["paramcd"] == paramcd].unique()]
        )
    )


    fig.add_annotation(x=1, y=alt_min + 0.21,text=f'{first_val} ULN',showarrow=False,font=dict(size=8),xref="paper")
    fig.add_annotation(x=1,y=ast_min + 0.21, text=f'{second_val} ULN', showarrow=False, font=dict(size=8), xref="paper")
    fig.add_annotation(showarrow=False,xref='paper', x=0, yref='paper',y=0.012,text=f"{second_val}",font=dict(size=12))
    fig.add_annotation(showarrow=False,xref='paper', x=0, yref='paper',y=0.05,text=f"{first_val}",font=dict(size=12))
    fig.add_annotation(showarrow=False,xref='paper', x=0.03, yref='paper',y=0.1,text="Change from Baseline",font=dict(size=14))
    fig.add_annotation(showarrow=False,xref='paper', x=-0.06, yref='paper',y=0.65,textangle=-90,text="Analysis value",font=dict(size=18))
    fig.add_annotation(showarrow=False,xref='paper', x=0.535, yref='paper',y= 0.17,text="Study day relative to treatment start day",font=dict(size=18))
    fig.add_annotation(showarrow=False,xref='paper', x=0.535, yref='paper',y= 1.05,text=f'Usubjid: {subjid}, Treatment: {filtered_raw["trta"].unique()[0]}',font=dict(size=18))


    return fig

@callback(Output("seriesplot", "figure"),
              [Input("usubjid", "value"),
               Input("first_paramcd", "value"),
               Input("second_paramcd", "value")])
def update_series_plot(subjid, first_val, second_val):
    return create_series_plot(subjid, first_val, second_val)

