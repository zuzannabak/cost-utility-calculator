# src/curves.py
"""
Fit y = a * log(b * x + 1)  (diminishing-returns curve)
Returns (a, b, r2).
"""

from typing import List, Tuple
import numpy as np
from scipy.optimize import minimize


def _log_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * np.log(b * x + 1.0)

# expose _log_model for testing
log_model = _log_model       # <- add this

def fit_log_curve(x: List[float], y: List[float]) -> Tuple[float, float, float]:
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    def loss(params):
        a, b = params
        return np.sum((_log_model(x_arr, a, b) - y_arr) ** 2)

    res = minimize(loss, x0=(1.0, 0.01), bounds=((0, None), (0, None)))
    a_hat, b_hat = res.x

    y_pred = _log_model(x_arr, a_hat, b_hat)
    sse = np.sum((y_pred - y_arr) ** 2)
    sst = np.sum((y_arr - y_arr.mean()) ** 2)
    r2 = 1.0 - sse / sst if sst else 0.0

    return float(a_hat), float(b_hat), float(r2)
