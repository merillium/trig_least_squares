import copy

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from numpy import cos, prod, sin, sinc, tan
from numpy.linalg import inv, lstsq


class TrigPolynomial:
    def __init__(self):
        self.polynomial_string = ""
        self.coefficient_string = ""
        self.polynomial_function = None

    ## this solves the least squares problem using trigonometric basis functions
    ## and generates a function that can be evaluated at x
    def trig_basis_functions(self, b1, b2, x):
        return [1, cos(b1 * x), sin(b2 * x)]

    def generate_lstsq_coefficients(self, x_vals, y_vals, b1, b2):
        ## we find the least squares solution to ATAx = ATb where b is the y_vals
        A = np.array([self.trig_basis_functions(b1, b2, x) for x in x_vals])

        ## default behavior: smallest possible values chosen for free variables (e.g. 0)
        coefs = lstsq(A, y_vals, rcond=None)[0]
        return coefs

    ## sets the polynomial_function attribute as a lambda function that can be evaluated at x
    def set_trig_polynomial(self, coefs, b1, b2):
        ## dot product of:
        # (1) the array generated from plugging x into basis function
        # (2) the coefficients generated from the solution to the least squares problem
        self.polynomial_function = lambda x: np.dot(
            coefs, self.trig_basis_functions(b1, b2, x)
        )
        
    def calculate_error(self, x_vals, y_vals):
        y_preds = [self.polynomial_function(x) for x in x_vals]
        error = np.sum(np.abs([y2 - y1 for y2, y1 in zip(y_vals, y_preds)]))
        return error

    def grid_search_polynomial_coefficients(
        self, x_vals, y_vals, b_min=0, b_max=2, grid_size=20
    ):

        ## optimize the best b1,b2 values for the polynomial to minimize error
        test_trig_polynomial = copy.deepcopy(self)

        ## initialize the error to None
        error = None
        for b1 in np.linspace(b_min, b_max, grid_size):
            for b2 in np.linspace(b_min, b_max, grid_size):

                ## generate coefs for the new iteration of the loop
                coefs = self.generate_lstsq_coefficients(x_vals, y_vals, b1, b2)

                ## this sets the polynomial and base level of error on the first iteration of the loop
                if error is None:
                    self.set_trig_polynomial(coefs, b1, b2)
                    test_trig_polynomial.set_trig_polynomial(coefs, b1, b2)
                    error = test_trig_polynomial.calculate_error(x_vals, y_vals)
                else:
                    test_trig_polynomial.set_trig_polynomial(coefs, b1, b2)
                    new_error = test_trig_polynomial.calculate_error(x_vals, y_vals)
                    if new_error < error:
                        error = new_error
                        b1_optimal, b2_optimal = b1, b2
                        print(
                            f"current optimal parameters: b1={b1_optimal} and b2={b2_optimal}"
                        )
                        coefs_optimal = coefs

        ## the optimal trig polynomial can be set outside of the grid search
        self.set_trig_polynomial(coefs_optimal, b1_optimal, b2_optimal)

        self.coefficient_string = (
            "$$\hat{y}(x) = \\begin{bmatrix} "
            + " & ".join(["{:.2f}".format(coef) for coef in coefs])
            + " \end{bmatrix} "
        )
        self.polynomial_string = (
            "\\begin{bmatrix} 1 & "
            + f"\cos {b1_optimal:.2f}x & \sin {b2_optimal:.2f}x"
            + " \end{bmatrix}^T$$"
        )
