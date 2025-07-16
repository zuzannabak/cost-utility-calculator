"""
Budget optimiser for the Cost-Utility Calculator.

Given unit prices, a total budget and (optionally) a GPU-hour cap, it
exhaustively searches for the split between labelling dollars and GPU
dollars that maximises the predicted accuracy.

Author: Zuzanna Bąk & ChatGPT · July 2025
"""
# ── src/optimizer.py ─────────────────────────────────────────────
from typing import Dict, Optional
import numpy as np

# helpers --------------------------------------------------------
def _eval_curve(a: float, b: float, x: float) -> float:
    return a * (1.0 - np.exp(-b * x))

def _combine(acc_lbl: float, acc_gpu: float) -> float:
    return 1.0 - (1.0 - acc_lbl) * (1.0 - acc_gpu)

# optimiser ------------------------------------------------------
def optimise_budget(
    *,
    label_cost: float,
    gpu_cost: float,
    budget: float,
    curve_label: Dict[str, float],
    curve_gpu: Dict[str, float],
    max_gpu_hours: Optional[float] = None,
    granularity: int = 1,
) -> Optional[Dict[str, float]]:
    """
    Search over money splits.  Returns the best dict or **None**
    when no allocation meets the GPU-hour cap.
    """
    budget = int(round(budget))
    best: Optional[Dict[str, float]] = None

    for label_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - label_dollars
        labels    = label_dollars / label_cost if label_cost else 0.0
        gpu_hours = gpu_dollars / gpu_cost   if gpu_cost   else 0.0

        if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
            continue  # infeasible → next grid-point

        acc = _combine(
            _eval_curve(curve_label["a"], curve_label["b"], labels),
            _eval_curve(curve_gpu["a"],  curve_gpu["b"],  gpu_hours),
        )

        if best is None or acc > best["accuracy"]:
            best = {
                "accuracy":      acc,
                "labels":        labels,
                "gpu_hours":     gpu_hours,
                "label_dollars": label_dollars,
                "gpu_dollars":   gpu_dollars,
            }

    return best                           # may be None


# legacy alias for older notebooks
optimize_budget = optimise_budget  # type: ignore
