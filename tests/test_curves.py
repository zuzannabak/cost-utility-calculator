import numpy as np
from src.curves import fit_log_curve

def test_fit_log_curve():
    rng = np.random.default_rng(42)
    x = np.linspace(0, 120, 10)
    y_true = 2 * np.log(0.05 * x + 1)
    y_noisy = y_true + rng.normal(0, 0.02, size=len(x))

    fit = fit_log_curve(x.tolist(), y_noisy.tolist())
    assert fit["rmse"] < 0.05, "RMSE should be small on synthetic data"
