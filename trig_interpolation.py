import numpy as np
from numpy import sin, cos, tan, sinc, prod
import pandas as pd
import plotly.graph_objects as go

## for testing purposes:
## unevenly spaced odd number of points
# x = [-2,-1,0,2,5]
# y = [-1,0,0,1,5]

# df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv")
# df["Date"] = pd.to_datetime(df["Date"])
# df["Days_passed"] = (df["Date"] - df["Date"][0]).dt.days

# x_plot = df.Days_passed.values.tolist()
# y_plot = df.Temp.values.tolist()

# idx_vals = [22, 167, 409, 565]
# x_train = [x_plot[idx] for idx in idx_vals]
# y_train = [y_plot[idx] for idx in idx_vals]

def get_odd_polynomial(x_vals, y_vals):
	"""return a function that can be evaluated at x for an odd number of points"""
	N = len(x_vals)
	K = int((N - 1)/2)
	def t_k(x, x_vals, k):
		return prod([sin((1/2)*(x-x_vals[m])) / sin((1/2)*(x_vals[k]-x_vals[m])) for m in range(int(2*K + 1)) if m != k])

	def eval_odd_polynomial(x):
		return sum([prod([y_vals[k], t_k(x, x_vals, k)]) for k in range(int(2*K + 1))])
	return eval_odd_polynomial

def get_even_polynomial(x_vals, y_vals):
	"""return a function that can be evaluated at x for an even number of points"""
	N = len(x_vals)
	K = int(N)/2
	def a_k(x_vals, k, epsilon=0.6):
		## WLOG we choose some epsilon such that sin((1/2)*epsilon) ≠ 0
		return x_vals[k] - epsilon

	def t_k(x, x_vals, k):
		first_term = sin((1/2)*(x - a_k(x_vals, k))) / sin((1/2)*(x_vals[k] - a_k(x_vals, k)))
		second_term = prod([sin((1/2)*(x-x_vals[m])) / sin((1/2)*(x_vals[k]-x_vals[m])) for m in range(int(2*K - 1 + 1)) if m != k]) # <--- list index out of range
		return first_term*second_term

	def eval_even_polynomial(x):
		return sum([prod([y_vals[k], t_k(x, x_vals, k)]) for k in range(int(2*K - 1 + 1))])
	return eval_even_polynomial

def generate_extrapolation_plot(x_plot, y_plot, x_train, y_train, x_range: list, num_points=100):
	## x_plot and y_plot are the data points that you are plotting
	## x_train and y_train are a subset of x_plot and y_plot used to generate the trig polynomial
	## x_min, x_max is used to generate the grid that is passed to the trig polynomial to plot the fitted function
	x_min, x_max = x_range
	x_grid = np.linspace(x_min, x_max, num_points)
	if len(x_train) % 2 == 1:
		print("creating odd polynomial...")
		odd_polynomial = get_odd_polynomial(x_train,y_train)
		y_grid = [odd_polynomial(x_grid_val) for x_grid_val in x_grid]
	if len(x_train) % 2 == 0:
		print("creating even polynomial...")
		even_polynomial = get_even_polynomial(x_train,y_train)
		y_grid = [even_polynomial(x_grid_val) for x_grid_val in x_grid]

	## create figure
	fig = go.Figure()

	## plot the data with markers
	fig.add_trace(go.Scatter(
		x=x_plot,
		y=y_plot,
		mode='markers',
		marker=dict(color='darkviolet'),
		name='data points'
		)
	)

	## plot the line of best fit using a grid
	fig.add_trace(go.Scatter(
		x=x_grid,
		y=y_grid,
		mode='lines',
		line=dict(color='salmon'),
		name='fitted function'
		)
	)

	fig.show()
