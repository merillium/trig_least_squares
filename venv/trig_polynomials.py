import numpy as np
from numpy import sin, cos, tan, sinc, prod
import pandas as pd
import plotly.graph_objects as go


class TrigPolynomial:
    def __init__(self):
        self.polynomial_string = ""
        self.coefficient_string = ""
        self.polynomial_function = None
    
    def get_polynomial(self, x_vals, y_vals):
        if len(x_vals) % 2 == 1:
            self.get_odd_polynomial(x_vals, y_vals)
        if len(x_vals) % 2 == 0:
            self.get_even_polynomial(x_vals, y_vals)
    
    def get_odd_polynomial(self, x_vals, y_vals):
        """return a function that can be evaluated at x for an odd number of points"""
        N = len(x_vals)
        K = int((N - 1)/2)
        def t_k(x, x_vals, k):
            return prod([sin((1/2)*(x-x_vals[m])) / sin((1/2)*(x_vals[k]-x_vals[m])) for m in range(int(2*K + 1)) if m != k])

        def eval_odd_polynomial(x):
            return sum([prod([y_vals[k], t_k(x, x_vals, k)]) for k in range(int(2*K + 1))])

        self.polynomial_string = f"$\displaystyle\sum_{{k=1}}^{{\\text{{{2*K}}}" + "} " +  f"{{y_k}}{{t_k}}(x) ,\ "
        self.coefficient_string = f"t_k(x)=\displaystyle\prod_{{m=0,\:m≠k}}^{{\\text{{{2*K}}}" + "} " +  r"\frac{{\sin\frac{{1}}{{2}}(x-x_m)}}{{\sin\frac{{1}}{{2}}(x_k-x_m)}}$"
        self.polynomial_function = eval_odd_polynomial

    def get_even_polynomial(self, x_vals, y_vals):
        """return a function that can be evaluated at x for an even number of points"""
        N = len(x_vals)
        K = int(N/2)
        def a_k(x_vals, k, epsilon=0.6):
            ## WLOG we choose some epsilon such that sin((1/2)*epsilon) ≠ 0, where epsilon = 2*phi 
            ## based on the derivation of the solution to the even polynomial here: https://en.wikipedia.org/wiki/Trigonometric_interpolation#Even_number_of_points
            return x_vals[k] - epsilon

        def t_k(x, x_vals, k):
            first_term = sin((1/2)*(x - a_k(x_vals, k))) / sin((1/2)*(x_vals[k] - a_k(x_vals, k)))
            second_term = prod([sin((1/2)*(x-x_vals[m])) / sin((1/2)*(x_vals[k]-x_vals[m])) for m in range(int(2*K - 1 + 1)) if m != k])
            return first_term*second_term

        def eval_even_polynomial(x):
            return sum([prod([y_vals[k], t_k(x, x_vals, k)]) for k in range(int(2*K - 1 + 1))])
        
        self.polynomial_string = f"$\displaystyle\sum_{{k=1}}^{{\\text{{{2*K - 1}}}" + "} " +  f"{{y_k}}{{t_k}}(x) ,\ "
        self.coefficient_string = f"t_k(x)= " + r"\displaystyle\frac{{\sin\frac{{1}}{{2}}(x-\alpha_k)}}{{\sin\frac{{1}}{{2}}(x_k-\alpha_k)}}" \
        + f"\displaystyle\prod_{{m=0,\:m≠k}}^{{\\text{{{2*K-1}}}" + "} " + r"\frac{{\sin\frac{{1}}{{2}}(x-x_m)}}{{\sin\frac{{1}}{{2}}(x_k-x_m)}} ,\ " \
        + r"\alpha_k=" + f"\displaystyle\sum_{{m=0\:m≠k}}^{{\\text{{{2*K-1}}}" + "} " + r"{{x_m}}-2\varphi_k ,\ \varphi_k = 0.6$"
        self.polynomial_function = eval_even_polynomial