import base64
import copy
import io
import re

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
from numpy.lib import polynomial

from trig_polynomials import TrigPolynomial
from years import from_date_to_year_fraction, from_year_fraction_to_date


def generate_extrapolation_fig(
    x_plot: list,
    y_plot: list,
    x_train: list,
    y_train: list,
    x_range: list,
    b_min: float = 0,
    b_max: float = 2,
    num_points=1000,
    time_series=False,
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
    error = None

    ## creates a trig polynomial of degree n that fits the data
    trig_polynomial.grid_search_polynomial_coefficients(x_train, y_train, b_min, b_max)
    y_grid = [trig_polynomial.polynomial_function(x_grid_val) for x_grid_val in x_grid]
    polynomial_equation = trig_polynomial.polynomial_string
    polynomial_coefficents = trig_polynomial.coefficient_string

    ## create figure
    fig = go.Figure()

    ## plot the trigonometric polynomial best fit function using a grid
    ## if time_series, then cast the x_grid and x_plot as timestamps
    ## and replace all variable instances of x with t
    if time_series:
        x_grid = [from_year_fraction_to_date(t) for t in x_grid]
        x_plot = [from_year_fraction_to_date(t) for t in x_plot]
        title = re.sub(r"(?<=[\d\(])x", "t", polynomial_coefficents + polynomial_equation)
    else:
        title = polynomial_coefficents + polynomial_equation

    ## plot the data with markers
    fig.add_trace(
        go.Scatter(
            x=x_plot,
            y=y_plot,
            mode="markers",
            marker=dict(color="darkviolet"),
            name="data points",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x_grid,
            y=y_grid,
            mode="lines",
            line=dict(color="salmon"),
            name="fitted function",
        )
    )

    fig.update_layout(title=title, margin=dict(l=0), font=dict(size=12))
    return fig


def create_dash_app(fig=go.Figure(dict(layout=dict(margin=dict(l=0))))):
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        external_scripts=[
            "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML",
        ],
    )

    app.layout = html.Div(
        [
            dcc.Graph(figure=fig, id="trig-polynomial-fig", mathjax=True),
            html.Div(
                [
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(
                            [
                                "Drag and Drop or ",
                                html.A("Select a csv file"),
                            ]
                        ),
                        max_size=10**6,
                        style={
                            "height": "60px",
                            "width": "300px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                        },
                    ),
                    html.H5(
                        "OR",
                        style={
                            "padding-left": "10px",
                            "padding-right": "10px",
                            "vertical-align": "middle",
                        },
                    ),
                    html.Button(
                        "Load stocks data set",
                        id="load-stocks",
                        n_clicks=0,
                        style={"height": "30px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "padding-left": "10px",
                    "align-items": "center",
                    "vertical-align": "middle",
                },
            ),
            html.Br(),
            html.Div(
                id="data-upload-message",
                style={
                    "whiteSpace": "pre-line",
                    "color": "red",
                    "padding-left": "10px",
                },
            ),
            html.Div(
                [
                    dcc.Dropdown(
                        id="x-column-dropdown",
                        options=[],
                        searchable=True,
                        placeholder="Select your x column",
                        style={"display": "inline-block", "width": "180px"},
                    ),
                    dcc.Dropdown(
                        id="y-column-dropdown",
                        options=[],
                        searchable=True,
                        placeholder="Select your y column",
                        style={"display": "inline-block", "width": "180px"},
                    ),
                ],
                style={"padding": "10px"},
            ),
            dcc.Checklist(["time series"], [], id="is-timeseries", style={"padding-left": "6px"}),
            html.Br(),
            dcc.Store(id="csv-data"),
            html.Div(
                [
                    dcc.Textarea(
                        className="xvalues-string",
                        id="xvalues-string",
                        value="",
                        placeholder="Enter x-values separated by commas",
                        style={"width": "175px", "height": 50, "resize": "none"},
                        draggable=False,
                    ),
                    dcc.Textarea(
                        id="yvalues-string",
                        placeholder="Enter y-values separated by commas",
                        value="",
                        style={"width": "175px", "height": 50, "resize": "none"},
                        draggable=False,
                    ),
                ],
                style={"padding-left": "10px"},
            ),
            html.H4("Enter the frequency range to search:", style={"padding-left": "10px"}),
            html.Div(
                [
                    dcc.Input(id="min-frequency", placeholder="Min frequency", type="number"),
                    dcc.Input(
                        id="max-frequency",
                        placeholder="Max frequency",
                        type="number",
                    ),
                ],
                style={"padding-left": "10px"},
            ),
            html.Br(),
            html.Div(
                [
                    html.Button(
                        "Generate extrapolation plot",
                        id="generate-plot",
                        n_clicks=0,
                        style={"whiteSpace": "pre-wrap"},
                    )
                ],
                style={"padding-left": "10px"},
            ),
            html.Br(),
            html.Div(
                id="error-output",
                style={
                    "whiteSpace": "pre-line",
                    "color": "red",
                    "padding-left": "10px",
                },
            ),
        ]
    )

    ## this callback processes the input and stores the dataframe
    @app.callback(
        Output("csv-data", "data"),
        Output("x-column-dropdown", "options"),
        Output("y-column-dropdown", "options"),
        Output("data-upload-message", "children"),
        Output("is-timeseries", "value"),
        Input("upload-data", "contents"),
        Input("load-stocks", "n_clicks"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def parse_csv_and_fill_dropdowns(contents, stocks_nclicks, filename):
        max_rows = 20000
        print(ctx.triggered_id)
        if ctx.triggered_id == "load-stocks":
            print("loading stocks dataset")
            df_stocks = pd.read_csv("./tests/stocks.csv")

            return (
                df_stocks.to_json(orient="split"),
                ["date"],
                ["GOOG", "AAPL", "AMZN", "FB", "NFLX", "MSFT"],
                "Stocks data successfully loaded!",
                ["time series"],
            )
        else:
            if not filename.endswith(".csv"):
                error_message = "Error: you must upload a .csv file"
                return None, [], [], error_message, []
            else:
                try:
                    content_type, content_string = contents.split(",")
                    decoded = base64.b64decode(content_string)
                    df_input = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                    if len(df_input) > max_rows:
                        error_message = (
                            f"The csv file exceeds the maximum allowable limit of {max_rows} rows"
                        )
                        return None, [], [], error_message, []
                    else:
                        all_cols = df_input.columns
                        dropdown_options = [{"label": col, "value": col} for col in all_cols]
                        return (
                            df_input.to_json(orient="split"),
                            dropdown_options,
                            dropdown_options,
                            "Data successfully loaded!",
                        )

                except Exception as e:
                    error_message = "Error: your csv file could not be processed"
                    return None, [], [], error_message, []

    ## this callback uses the selected x- and y- columns of the stored dataframe to populate the textboxes
    @app.callback(
        Output("xvalues-string", "value"),
        Output("yvalues-string", "value"),
        Input("csv-data", "data"),
        Input("x-column-dropdown", "value"),
        Input("y-column-dropdown", "value"),
        prevent_initial_call=True,
    )
    def fill_textboxes(csv_data, x_col, y_col):
        if csv_data == None:
            return "", ""
        if (x_col == None) & (y_col == None):
            return "", ""
        elif (x_col == None) & (y_col != None):
            df_input = pd.read_json(csv_data, orient="split")
            df_input = df_input.astype(str)
            y_values = ",".join(df_input[y_col].tolist())
            return "", y_values
        elif (x_col != None) & (y_col == None):
            df_input = pd.read_json(csv_data, orient="split")
            df_input = df_input.astype(str)
            x_values = ",".join(df_input[x_col].tolist())
            return x_values, ""
        else:
            df_input = pd.read_json(csv_data, orient="split")
            df_input = df_input.astype(str)
            x_values = ",".join(df_input[x_col].tolist())
            y_values = ",".join(df_input[y_col].tolist())
            return x_values, y_values

    ## this callback processes the x-values and y-values textboxes and creates the figure
    @app.callback(
        Output("trig-polynomial-fig", "figure"),
        Output("error-output", "children"),
        Input("generate-plot", "n_clicks"),
        [
            State("is-timeseries", "value"),
            State("min-frequency", "value"),
            State("max-frequency", "value"),
            State("xvalues-string", "value"),
            State("yvalues-string", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_graph(
        n_clicks,
        is_timeseries,
        min_frequency,
        max_frequency,
        xvalues_string,
        yvalues_string,
    ):
        ## return figure, rendered polynomial latex string, and empty error message
        ## keep the default text when the app first loads
        ## when there is any type of error, remove the equations (by resetting the title text and changing the color to white)

        ## load an empty plot before any x or v-values are processed
        # if n_clicks == 0:
        #     return go.Figure(dict(layout=dict(margin=dict(l=0)))), ""

        ## ensure numbers have been entered for x and y values
        try:
            ## convert string of timestamps to epoch in ns (since 1970-01-01)
            if len(is_timeseries) == 0:
                time_series = False
                xvalues_list = [float(val) for val in xvalues_string.split(",")]
            else:
                time_series = True
                xvalues_list = [from_date_to_year_fraction(d) for d in xvalues_string.split(",")]

        except ValueError as e:
            error_message = "Error: invalid x-value input!"
            return dash.no_update, error_message
        try:
            yvalues_list = [float(val) for val in yvalues_string.split(",")]
        except ValueError as e:
            error_message = "Error: invalid y-value input!"
            return dash.no_update, error_message
        if len(xvalues_list) != len(yvalues_list):
            error_message = "Error: there must be an equal number of x- and y-values!"
            return dash.no_update, error_message
        elif min_frequency == None:
            error_message = "Error: you must specify a min frequency"
            return dash.no_update, error_message
        elif max_frequency == None:
            error_message = "Error: you must specify a max frequency"
            return dash.no_update, error_message
        elif min_frequency > max_frequency:
            error_message = "Error: min frequency must be less than max frequency"
            return dash.no_update, error_message
        elif (min_frequency < 0) | (max_frequency < 0):
            error_message = "Error: min and max frequency must be non-negative"
            return dash.no_update, error_message
        else:
            x_range_padding = (max(xvalues_list) - min(xvalues_list)) / 2
            x_range = [
                min(xvalues_list) - x_range_padding,
                max(xvalues_list) + x_range_padding,
            ]
            fig = generate_extrapolation_fig(
                x_plot=xvalues_list,
                y_plot=yvalues_list,
                x_train=xvalues_list,
                y_train=yvalues_list,
                x_range=x_range,
                b_min=min_frequency,
                b_max=max_frequency,
                time_series=time_series,
            )
            return fig, ""

    return app


## set debug=False when deploying live
if __name__ == "__main__":
    app = create_dash_app()
    app.run_server(debug=False, host="0.0.0.0", port=8080)
