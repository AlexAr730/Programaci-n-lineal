import re
import pandas as pd
import time
from IPython.display import clear_output, display
import plotly.graph_objects as go

def parse_objective_function(objective_function):
    objective_function = objective_function.replace(" ", "")
    if objective_function[0] not in ["+", "-"]:
        objective_function = "+" + objective_function

    # Encuentra términos como +3x, -4.5y, etc.
    terms = re.findall(r"([+-]?\d*\.?\d*)([a-zA-Z])", objective_function)

    coefficients = []
    for coef_str, var in terms:
        # Si no hay número explícito, se asume 1 o -1
        if coef_str in ['+', '-']:
            coef_str += '1'
        elif coef_str == '':
            coef_str = '1'

        try:
            coef = float(coef_str)
        except ValueError:
            coef = 0.0
        coefficients.append(coef)

    return coefficients