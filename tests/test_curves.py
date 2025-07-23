# tests/test_curves.py
import os
import sys

import numpy as np

from src.cucal.curves import fit_log_curve

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_fit_log_curve():
    # synthetic data: a=2, b=0.05  + small noise
    rng = np.random.default_rng(42)
    x = np.linspace(0, 120, 10)
    y_true = 2 * np.log(0.05 * x + 1)
    y_noisy = y_true + rng.normal(0, 0.02, size=len(x))

    fit = fit_log_curve(x.tolist(), y_noisy.tolist())  # returns dict

    rmse = fit["rmse"]
    a_hat = fit["a"]
    b_hat = fit["b"]

    assert rmse < 0.05, "RMSE should be very small"
    assert abs(a_hat - 2) < 0.1
    assert abs(b_hat - 0.05) < 0.01
