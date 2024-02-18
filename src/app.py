'''
 # @ Create Time: 2024-02-15 14:19:06.559386
'''
from dash import Dash, html, dcc
import dash


external_css = ["assets/style.css"]

app = dash.Dash(__name__, use_pages=True, external_stylesheets=external_css, title="PortfolioDash")
server = app.server

    
img_tag = html.Img(src="assets/cc.svg", width=250, height=250)
brand_link = html.A(img_tag, href="https://www.armatanalytics.com/", className="navbar-left")
pages_links = [dcc.Link(page['name'], href=page["relative_path"], className="nav-link fs-5 navbar-right")
               for page in dash.page_registry.values() if page["name"] != "Not found 404"]



app.layout = html.Div([
    html.Nav(children=[
        html.Div([
            html.Div([brand_link, ] + pages_links, className="navbar")
        ]),
    ]),
    html.Div(style={"height": "10px", "background-color": "#e6e6e6"}),
    html.Div([
        html.Br(),
        dash.page_container
    ]),
])

if __name__ == '__main__':
    app.run(debug=False)
