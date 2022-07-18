import base64
import io
import numpy as np
import pandas as pd
from numpy.lib import polynomial
import dash
from dash import dcc, html, Input, Output, ctx, State
import plotly.graph_objects as go

from trig_polynomials import TrigPolynomial
from years import from_date_to_year_fraction, from_year_fraction_to_date

def generate_extrapolation_fig(
        x_plot: list, 
        y_plot: list, 
        x_train: list, 
        y_train: list, 
        x_range: list, 
        n: float, 
        num_points=1000,
        time_series=False
    ) -> go.Figure:
    ## x_plot and y_plot are the data points that you are plotting
    ## x_train and y_train are a subset of x_plot and y_plot used to generate the trig polynomial
    ## x_min, x_max is used to generate the grid that is passed to the trig polynomial to plot the fitted function
    ## even if x_plot, x_train are meant to be timestamps, they should be passed to this function as floats

    x_min, x_max = x_range
    x_grid = np.linspace(x_min, x_max, num_points)

    ## instantiate an object of the TrigPolynomial class
    ## it contains the interpolation function and also a string representation of the polynomial
    trig_polynomial = TrigPolynomial()

    ## this constructs a trigonometric polynomial that interpolates all points perfectly
    ## the behavior of such interpolating functions are too sensitive to have practical applications
    if n == float("inf"):
        trig_polynomial.get_polynomial(x_train, y_train)
    
    ## creates a trig polynomial of degree n that fits the data
    else:
        n = int(n)
        coefs = trig_polynomial.generate_lstsq_coefficients(x_train, y_train, int(n))
        trig_polynomial.get_degree_n_polynomial(coefs, n)
    
    y_grid = [trig_polynomial.polynomial_function(x_grid_val) for x_grid_val in x_grid]
    polynomial_equation = trig_polynomial.polynomial_string
    polynomial_coefficents = trig_polynomial.coefficient_string

    ## create figure
    fig = go.Figure()

    ## plot the trigonometric polynomial best fit function using a grid
    ## if time_series, then cast the x_grid and x_plot as timestamps
    if time_series:
        x_grid = [from_year_fraction_to_date(t) for t in x_grid]
        x_plot = [from_year_fraction_to_date(t) for t in x_plot]

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

    ## this workaround using MathJax allows LaTeX style equations to be displayed
    ## source: https://github.com/plotly/dash/issues/242
    fig.update_layout(title=polynomial_coefficents + polynomial_equation, margin=dict(l=0), font=dict(size=12))
    return fig

def create_dash_app(fig=go.Figure()):
    app = dash.Dash(__name__, suppress_callback_exceptions=True,
    external_scripts=[
        'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',
    ])

    app.layout = html.Div([
        dcc.Graph(figure=fig, id='trig-polynomial-fig', mathjax=True),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a csv file')
            ]),
            max_size=10**6,
            style={
                'width': '30%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
            }
        ),
        html.Br(),
        html.Div(id='error-data-upload', style={'whiteSpace': 'pre-line', 'color': 'red'}),
        html.Br(),
        dcc.Checklist(
            ['time series'],
            [],
            id='is-timeseries',
        ),
        html.Br(),
        html.Div(
            dcc.Dropdown(
                id='x-column-dropdown',
                options=[],
                searchable=True,
                placeholder='Select your x column'
            ),
            style={"width": "15%"}
        ),
        html.Div(
            dcc.Dropdown(
                id='y-column-dropdown',
                options=[],
                searchable=True,
                placeholder='Select your y column'
            ),
            style={"width": "15%"}
        ),
        html.Br(),
        dcc.Store(id="csv-data"),
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
        html.Div(
            dcc.Dropdown(
                id='polynomial-degree',
                options=[val for val in range(1,11)],
                value=1,
                searchable=False,
                placeholder='Select a polynomial degree'
            ),
            style={"width": "15%"}
        ),
        html.Br(),
        # dcc.Slider(
        #     0, 100, 5,
        #     value=1,
        #     id='test'
        # ),
        html.Br(),
        html.Button('Generate extrapolation plot', id='generate-plot', n_clicks=0, style={'whiteSpace': 'pre-wrap'}),
        html.Br(),
        html.Div(id='error-output', style={'whiteSpace': 'pre-line', 'color': 'red'})
    ],id="outer")

    ## this callback processes the input and stores the dataframe
    @app.callback(
        Output('csv-data', 'data'),
        Output('x-column-dropdown', 'options'),
        Output('y-column-dropdown', 'options'),
        Output('error-data-upload', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def parse_csv_and_fill_dropdowns(contents, filename):
        max_rows = 20000
        if not filename.endswith('.csv'):
            error_message = "Error: you must upload a .csv file"
            return None, [], [], error_message
        else:
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df_input = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                if len(df_input) > max_rows:
                    error_message = f"The csv file exceeds the maximum allowable limit of {max_rows} rows"
                    return None, [], [], error_message
                else:
                    all_cols = df_input.columns
                    dropdown_options = [{'label': col, 'value': col} for col in all_cols]
                    return df_input.to_json(orient='split'), dropdown_options, dropdown_options, "Data successfully parsed!"
                    
            except Exception as e:
                error_message = "Error: your csv file could not be processed"
                return None, [], [], error_message

            
    ## this callback uses the selected x- and y- columns of the stored dataframe to populate the textboxes
    @app.callback(
        Output('xvalues-string', 'value'),
        Output('yvalues-string', 'value'),
        Input('csv-data', 'data'),
        Input('x-column-dropdown', 'value'),
        Input('y-column-dropdown', 'value'),
        prevent_initial_call=True
    )
    def fill_textboxes(csv_data, x_col, y_col):
        if csv_data == None:
            return "", ""
        if (x_col == None) & (y_col == None):
            return "", ""
        elif (x_col == None) & (y_col != None):
            df_input = pd.read_json(csv_data, orient='split')
            df_input = df_input.astype(str)
            y_values = ",".join(df_input[y_col].tolist())
            return "", y_values
        elif (x_col != None) & (y_col == None):
            df_input = pd.read_json(csv_data, orient='split')
            df_input = df_input.astype(str)
            x_values = ",".join(df_input[x_col].tolist())
            return x_values, ""
        else:
            df_input = pd.read_json(csv_data, orient='split')
            df_input = df_input.astype(str)
            x_values = ",".join(df_input[x_col].tolist())
            y_values = ",".join(df_input[y_col].tolist())
            return x_values, y_values

    ## this callback processes the x-values and y-values textboxes and creates the figure
    @app.callback(
        Output('trig-polynomial-fig', 'figure'),
        Output('error-output', 'children'),
        Input('generate-plot', 'n_clicks'),
        [State('polynomial-degree', 'value'),
         State('is-timeseries', 'value'),
         State('xvalues-string', 'value'),
         State('yvalues-string', 'value')]
    )
    def update_graph(n_clicks, polynomial_degree, is_timeseries, xvalues_string, yvalues_string):
        ## return figure, rendered polynomial latex string, and empty error message
        ## keep the default text when the app first loads
        ## when there is any type of error, remove the equations (by resetting the title text and changing the color to white)

        ## load an empty plot before any x or v-values are processed
        if n_clicks == 0:
             return go.Figure(dict(layout=dict(margin=dict(l=0)))), ""
        ## check that a dropdown option has been selected
        if polynomial_degree == None:
            error_message = "Error: select a polynomial degree"
            return go.Figure(dict(layout=dict(title=dict(text="-",font=dict(color='white'))), margin=dict(l=0))), error_message
        
        ## ensure numbers have been entered for x and y values
        try:
            ## convert string of timestamps to epoch in ns (since 1970-01-01)
            if len(is_timeseries) == 0:
                time_series = False
                xvalues_list = [float(val) for val in xvalues_string.split(',')]
            else:
                time_series = True
                xvalues_list = [from_date_to_year_fraction(d) for d in xvalues_string.split(',')]
                
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
        
        ## float("inf") is no longer an option so this condition never occurs
        elif (len(xvalues_list) != len(set(xvalues_list))) & (float(polynomial_degree) == float("inf")):
            error_message = "Error: cannot fit a polynomial to duplicate x-values"
            return go.Figure(dict(layout=dict(title=dict(text="-",font=dict(color='white'))), margin=dict(l=0))), error_message
        else:
            x_range_padding = (max(xvalues_list) - min(xvalues_list)) / 2
            x_range = [min(xvalues_list)-x_range_padding, max(xvalues_list)+x_range_padding]
            fig = generate_extrapolation_fig(
                x_plot=xvalues_list, 
                y_plot=yvalues_list, 
                x_train=xvalues_list, 
                y_train=yvalues_list, 
                x_range=x_range, 
                n=float(polynomial_degree),
                time_series=time_series
            )
            return fig, ""

    return app

## set debug=False when deploying live
if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=True, host="0.0.0.0", port=8080)
