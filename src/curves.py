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
    x, y = np.asarray(x, float), np.asarray(y, float)

    res = minimize(lambda p: np.sum((log_model(x, *p) - y)**2),
                   x0=(1.0, 0.01), bounds=((0,None),(0,None)))
    a, b = map(float, res.x)        # ← ensure native Python floats

    rmse = float(np.sqrt(np.mean((log_model(x, a, b) - y)**2)))
    return a, b, rmse

