# ── src/curves.py ────────────────────────────────────────────────────────────
"""
Fit y = a * log(b * x + 1)     (diminishing returns)
Returns (a, b, r2).

  a : max achievable metric (≈ plateau)
  b : controls curvature / speed of saturation
"""

from typing import List, Tuple
import numpy as np
from scipy.optimize import minimize


def log_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Vectorised log curve."""
    return a * np.log1p(b * x)          # log1p is numerically safer


from sklearn.metrics import root_mean_squared_error

def fit_log_curve(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)

    # Fit as before...
    res = minimize(lambda p: np.sum((log_model(x, *p) - y)**2),
                   x0=(1.0, 0.01), bounds=((0,None),(0,None)))
    a, b = res.x

    y_hat = log_model(x, a, b)
    rmse  = root_mean_squared_error(y, y_hat)  # ← replace R²
    return a, b, rmse

