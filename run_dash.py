import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import webbrowser
from threading import Timer
import plotly.graph_objects as go
from trig_polynomials import get_odd_polynomial, get_even_polynomial

def generate_extrapolation_fig(x_plot, y_plot, x_train, y_train, x_range: list, num_points=500):
    ## x_plot and y_plot are the data points that you are plotting
    ## x_train and y_train are a subset of x_plot and y_plot used to generate the trig polynomial
    ## x_min, x_max is used to generate the grid that is passed to the trig polynomial to plot the fitted function
    x_min, x_max = x_range
    x_grid = np.linspace(x_min, x_max, num_points)
    if len(x_train) % 2 == 1:
        # print("creating odd polynomial...")
        odd_polynomial = get_odd_polynomial(x_train,y_train)
        y_grid = [odd_polynomial(x_grid_val) for x_grid_val in x_grid]
    if len(x_train) % 2 == 0:
        # print("creating even polynomial...")
        even_polynomial = get_even_polynomial(x_train,y_train)
        y_grid = [even_polynomial(x_grid_val) for x_grid_val in x_grid]

    ## create figure
    fig = go.Figure()

    ## plot the line of best fit using a grid
    fig.add_trace(go.Scatter(
        x=x_grid,
        y=y_grid,
        mode='lines',
        line=dict(color='salmon'),
        name='fitted function'
        )
    )

    ## plot the data with markers
    fig.add_trace(go.Scatter(
        x=x_plot,
        y=y_plot,
        mode='markers',
        marker=dict(color='darkviolet'),
        name='data points'
        )
    )

    return fig

def create_dash_app(fig=go.Figure()):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(figure=fig, id='trig-polynomial-fig'),
        dcc.Textarea(
            id='xvalues-string',
            value='1,2,3',
            style={'width': '10%', 'height': 50},
            draggable=False
        ),
        dcc.Textarea(
            id='yvalues-string',
            value='1,2,3',
            style={'width': '10%', 'height': 50},
            draggable=False
        ),
        html.Br(),
        html.Button('Generate extrapolation plot', id='generate-plot', n_clicks=0, style={'whiteSpace': 'pre-wrap'}),
        html.Br(),
        html.Div(id='error-output', style={'whiteSpace': 'pre-line', 'color': 'red'})
    ])

    @app.callback(
        Output('trig-polynomial-fig', 'figure'),
        Output('error-output', 'children'),
        [Input('generate-plot', 'n_clicks')],
        state=[State('xvalues-string', 'value'),
         State('yvalues-string', 'value')]
    )
    def update_graph(n_clicks, xvalues_string, yvalues_string):
        try:
            xvalues_list = [float(val) for val in xvalues_string.split(',')]
        except ValueError as e:
            error_message = "Error: invalid x-value input!"
            return go.Figure(), error_message
        try:
            yvalues_list = [float(val) for val in yvalues_string.split(',')]
        except ValueError as e:
            error_message = "Error: invalid y-value input!"
            return go.Figure(), error_message
        if len(xvalues_list) != len(yvalues_list):
            error_message = "Error: there must be an equal number of x- and y-values!"
            return go.Figure(), error_message
        elif len(xvalues_list) != len(set(xvalues_list)):
            error_message = "Error: cannot fit a polynomial to duplicate x-values"
            return go.Figure(), error_message
        else:
            x_range = [min(xvalues_list)-5, max(xvalues_list)+5]
            fig = generate_extrapolation_fig(xvalues_list, yvalues_list, xvalues_list, yvalues_list, x_range)
            return fig, ""

    return app

def open_browser(port=8050):
    webbrowser.open_new(f"http://127.0.0.1:{port}/")

if __name__ == '__main__':
    Timer(1, open_browser).start();
    app = create_dash_app()
    app.run_server(debug=True, use_reloader=False)
