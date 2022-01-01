import numpy as np
from numpy.lib import polynomial
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from trig_polynomials import TrigPolynomial

def generate_extrapolation_fig(x_plot: list, y_plot: list, x_train: list, y_train: list, x_range: list, num_points=500) -> go.Figure:
    ## x_plot and y_plot are the data points that you are plotting
    ## x_train and y_train are a subset of x_plot and y_plot used to generate the trig polynomial
    ## x_min, x_max is used to generate the grid that is passed to the trig polynomial to plot the fitted function
    x_min, x_max = x_range
    x_grid = np.linspace(x_min, x_max, num_points)

    ## instantialiate an object of the TrigPolynomial class
    ## it contains the interpolation function and also a string representation of the polynomial
    trig_polynomial = TrigPolynomial()
    trig_polynomial.get_polynomial(x_train,y_train)
    y_grid = [trig_polynomial.polynomial_function(x_grid_val) for x_grid_val in x_grid]
    polynomial_equation = trig_polynomial.polynomial_string
    polynomial_coefficents = trig_polynomial.coefficient_string
    
    ## create figure
    fig = go.Figure()

    ## plot the trigonometric polynomial interpolation using a grid
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

    ## this workaround using MathJax does indeed allow LaTeX style equations to be displayed
    ## source: https://github.com/plotly/dash/issues/242
    fig.update_layout(title=polynomial_equation + polynomial_coefficents, margin=dict(l=0))
    return fig

def create_dash_app(fig=go.Figure()):
    app = dash.Dash(__name__, external_scripts=[
        'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',
    ])

    app.layout = html.Div([
        dcc.Graph(figure=fig, id='trig-polynomial-fig'),
        dcc.Textarea(
            id='xvalues-string',
            value="",
            placeholder='Enter x-values separated by commas',
            style={'width': '15%', 'height': 50},
            draggable=False
        ),
        dcc.Textarea(
            id='yvalues-string',
            placeholder="Enter y-values separated by commas",
            value="",
            style={'width': '15%', 'height': 50},
            draggable=False
        ),
        html.Br(),
        html.Button('Generate extrapolation plot', id='generate-plot', n_clicks=0, style={'whiteSpace': 'pre-wrap'}),
        html.Br(),
        html.Div(id='error-output', style={'whiteSpace': 'pre-line', 'color': 'red'})
    ],id="outer")

    @app.callback(
        Output('trig-polynomial-fig', 'figure'),
        Output('error-output', 'children'),
        [Input('generate-plot', 'n_clicks')],
        [State('xvalues-string', 'value'),
         State('yvalues-string', 'value')]
    )
    def update_graph(n_clicks, xvalues_string, yvalues_string):
        ## return figure, rendered polynomial latex string, and empty error message
        ## keep the default text when the app first loads
        ## when there is any type of error, remove the equations (by resetting the title text and changing the color to white)
        if n_clicks == 0:
            return go.Figure(dict(layout=dict(margin=dict(l=0)))), ""
        try:
            xvalues_list = [float(val) for val in xvalues_string.split(',')]
        except ValueError as e:
            error_message = "Error: invalid x-value input!"
            return go.Figure(dict(layout=dict(title=dict(text="-",font=dict(color='white'))), margin=dict(l=0))), error_message
        try:
            yvalues_list = [float(val) for val in yvalues_string.split(',')]
        except ValueError as e:
            error_message = "Error: invalid y-value input!"
            return go.Figure(dict(layout=dict(title=dict(text="-",font=dict(color='white'))), margin=dict(l=0))), error_message
        if len(xvalues_list) != len(yvalues_list):
            error_message = "Error: there must be an equal number of x- and y-values!"
            return go.Figure(dict(layout=dict(title=dict(text="-",font=dict(color='white'))), margin=dict(l=0))), error_message
        elif len(xvalues_list) != len(set(xvalues_list)):
            error_message = "Error: cannot fit a polynomial to duplicate x-values"
            return go.Figure(dict(layout=dict(title=dict(text="-",font=dict(color='white'))), margin=dict(l=0))), error_message
        else:
            x_range = [min(xvalues_list)-5, max(xvalues_list)+5]
            fig = generate_extrapolation_fig(xvalues_list, yvalues_list, xvalues_list, yvalues_list, x_range)
            return fig, ""

    return app

if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=False, host="0.0.0.0", port=8080)
