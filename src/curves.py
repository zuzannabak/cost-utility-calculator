# src/curves.py
import numpy as np
from typing import List, Tuple

def fit_log_curve(x: List[float], y: List[float]) -> Tuple[float, float]:
    """
    Fit y = a * log(b*x + 1) using least squares.
    Return (a, b) parameters.
    """
    x_arr = np.array(x)
    y_arr = np.array(y)

    def model(params):
        a, b = params
        return a * np.log(b * x_arr + 1)

    def loss(params):
        return np.sum((model(params) - y_arr) ** 2)

    from scipy.optimize import minimize
    res = minimize(loss, x0=[1.0, 0.01], bounds=[(0, None), (0, None)])
    return tuple(res.x)
