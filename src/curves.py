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


from scipy.optimize import minimize, Bounds

def fit_log_curve(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    # ---------- loss ----------
    def loss(p):
        a, b = p
        return np.sum((log_model(x, a, b) - y) ** 2)

    # ---------- optimise ----------
    a0 = y.max() * 1.05                 # initial a just above plateau
    b0 = 5.0 / (x.mean() + 1)           # knee near mid-range
    res = minimize(loss, x0=(a0, b0), bounds=((0, None), (1e-4, 1e3)))

    a_hat, b_hat = res.x
    rmse = np.sqrt(loss((a_hat, b_hat)) / len(x))
    return {"a": float(a_hat), "b": float(b_hat), "rmse": float(rmse)}
