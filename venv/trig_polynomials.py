import numpy as np
from numpy import sin, cos, tan, sinc, prod
import pandas as pd
import plotly.graph_objects as go

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
        second_term = prod([sin((1/2)*(x-x_vals[m])) / sin((1/2)*(x_vals[k]-x_vals[m])) for m in range(int(2*K - 1 + 1)) if m != k])
        return first_term*second_term

    def eval_even_polynomial(x):
        return sum([prod([y_vals[k], t_k(x, x_vals, k)]) for k in range(int(2*K - 1 + 1))])
    return eval_even_polynomial

