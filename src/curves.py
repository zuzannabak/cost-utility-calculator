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
    
    def loss(p):
        a,b = p
        return np.sum((log_model(x, a, b) - y)**2)

    # sensible initial guess
    a0 = y.max()*1.05          # just above the plateau
    b0 = 5.0 / (np.mean(x)+1)  # bends the knee around the middle

    # hard lower bound keeps b ≥ 1e-4
    bounds = Bounds([0.3*a0, 1e-4], [2.0*a0, 1e3])

    res   = minimize(loss, x0=(a0, b0), bounds=bounds)
    a,b   = res.x
    rmse  = np.sqrt(loss((a,b))/len(x))
    return a,b,rmse

