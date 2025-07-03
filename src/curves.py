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

# keep log_model at top
def log_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Vectorised log curve."""
    return a * np.log1p(b * x)   # log1p = log(1+x)

from sklearn.metrics import mean_squared_error  # after top-level imports

def fit_log_curve(x, y):
    """Return dict with a, b, rmse."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    res = minimize(lambda p: np.sum((log_model(x, *p) - y) ** 2),
                   x0=(1.0, 0.01),
                   bounds=((0, None), (0, None)))
    a, b = res.x
    rmse = mean_squared_error(y, log_model(x, a, b), squared=False)
    return {"a": a, "b": b, "rmse": rmse}
