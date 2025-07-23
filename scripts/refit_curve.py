#!/usr/bin/env python3
"""
Fit a saturating log curve  a · (1 - exp(-b·x))  to (x, accuracy%) points
and print a, b, and RMSE in 0–1 units.

Usage:
    python scripts/refit_curve.py data/raw/kang2023.csv
"""
import sys, numpy as np
from pathlib import Path
from scipy.optimize import curve_fit

def model(x, a, b):
    return a * (1 - np.exp(-b * x))

def main(path: Path):
    data = np.loadtxt(path, delimiter=",")
    x      = data[:, 0]
    y_frac = data[:, 1] / 100            # convert % → fraction 0–1

    (a, b), _ = curve_fit(model, x, y_frac, p0=(0.9, 0.01))
    pred      = model(x, a, b)
    rmse      = float(np.sqrt(((pred - y_frac) ** 2).mean()))

    print(f"Fit parameters for {path.name}:")
    print(f"   a = {a:.6f}")
    print(f"   b = {b:.6f}")
    print(f"   RMSE (0–1 scale) = {rmse:.6f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Give exactly one CSV path!")
    main(Path(sys.argv[1]))
