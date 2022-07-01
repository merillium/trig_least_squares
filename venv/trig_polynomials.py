import numpy as np
from numpy import sin, cos, tan, sinc, prod
from numpy.linalg import inv, lstsq
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
    
    ## this solves the least squares problem using trigonometric basis functions
    ## and generates a function that can be evaluated at x
    def trig_basis_functions(self, x, n):
        basis_functions = [1]
        for k in range(1,n+1):
            basis_functions.extend([cos(k*x),sin(k*x)])
        return basis_functions
    
    def generate_lstsq_coefficients(self, x_vals, y_vals, n):
        ## we find the least squares solution to ATAx = ATb where b is the y_vals
        A = np.array([self.trig_basis_functions(x,n) for x in x_vals])
    
        ## default behavior: smallest possible values chosen for free variables (e.g. 0)
        coefs = lstsq(A,y_vals,rcond=None)[0]
        return coefs
        
    ## return a function that can be evaluated at x
    ## the coefficients should already be calculated ahead of time
    ## to ensure that we aren't re-calculating the coefficients which only depend on x_vals, y_vals, n
    def get_degree_n_polynomial(self, coefs, n):
        ## dot product of: 
        # (1) the array generated from plugging x into basis function
        # (2) the coefficients generated from the solution to the least squares problem
        self.polynomial_function = lambda x: np.dot(coefs, self.trig_basis_functions(x,n))
    