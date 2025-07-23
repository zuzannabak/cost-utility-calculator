#!/usr/bin/env python3
"""
Fit a saturating curve to a CSV with two columns (x, y).

Examples
--------
# labels (cost per label = 0.02 $)
python scripts/fit_curve.py \
       --csv data/raw/dragut/labels.csv \
       --task Dragut-2019-label        \
       --curve-type label              \
       --cost-per-unit 0.02

# GPU hours (cost per GPU-h = 1.40 $)
python scripts/fit_curve.py \
       --csv data/raw/dragut/gpu.csv \
       --task Dragut-2019-gpu       \
       --curve-type gpu             \
       --cost-per-unit 1.40
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import t


def sat(x: np.ndarray, a: float, b: float) -> np.ndarray:  # saturating curve
    return a * (1.0 - np.exp(-b * x))


# ---------- CLI ----------
cli = argparse.ArgumentParser()
cli.add_argument("--csv", required=True, help="CSV with two columns x,y")
cli.add_argument("--task", required=True, help='e.g. "Dragut-2019-label"')
cli.add_argument(
    "--curve-type",
    choices=["label", "gpu"],
    required=True,
    help="Determines JSON field: label_curve or gpu_curve",
)
cli.add_argument("--cost-per-unit", type=float, required=True)
cli.add_argument("--out", default="data/curves.json")
args = cli.parse_args()

# ---------- Fit ----------
df = pd.read_csv(args.csv, header=None)
x = df.iloc[:, 0].to_numpy()
y = df.iloc[:, 1].to_numpy()

(a, b), cov = curve_fit(sat, x, y, p0=(0.8, 0.0005), maxfev=20_000)
pred = sat(x, a, b)
rmse = float(np.sqrt(((pred - y) ** 2).mean()))

# 95 % CI for each point (optional, but nice to have)
alpha = 0.05
n = len(x)
dof = max(0, n - 2)
tval = t.ppf(1 - alpha / 2, dof)
residual_std = np.sqrt(((y - pred) ** 2).sum() / dof)
ci_low = float(pred.mean() - tval * residual_std / np.sqrt(n))
ci_high = float(pred.mean() + tval * residual_std / np.sqrt(n))

# ---------- Write ----------
out_p = Path(args.out)
out_p.parent.mkdir(parents=True, exist_ok=True)
curves = json.loads(out_p.read_text()) if out_p.exists() else {}

entry = curves.setdefault(args.task, {})
entry[f"{args.curve_type}_curve"] = {"a": float(a), "b": float(b)}
entry["rmse"] = rmse
entry["ci_low"] = ci_low
entry["ci_high"] = ci_high
entry["cost_per_unit"] = args.cost_per_unit

out_p.write_text(json.dumps(curves, indent=2))
print(
    f"✅  {args.task}: a={a:.4f}  b={b:.6f}  rmse={rmse:.4f} "
    f"→ {args.out} ({args.curve_type}_curve)"
)
