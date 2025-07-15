"""
Budget optimiser for the Cost-Utility Calculator.

Given unit prices, a total budget and (optionally) a GPU-hour cap, it
exhaustively searches for the split between labelling dollars and GPU
dollars that maximises the predicted accuracy.

Author: Zuzanna Bąk & ChatGPT · July 2025
"""
from typing import Dict, Optional

import numpy as np


# ────────────────────────────────────────────────────────────── helpers ─────
def _eval_curve(a: float, b: float, x: float) -> float:
    """Generic saturating-log curve:  a * (1 – e^{-b·x})."""
    return a * (1.0 - np.exp(-b * x))


def _combine(acc_label: float, acc_gpu: float) -> float:
    """
    Combine two independent accuracy contributions.

    Heuristic: complements multiply ⇒
        1 – (1-acc_lbl)(1-acc_gpu)
    Feel free to replace this rule later.
    """
    return 1.0 - (1.0 - acc_label) * (1.0 - acc_gpu)


# ───────────────────────────────────────────────────────── optimiser ────────
def optimise_budget(  # British spelling = public API
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
    Grid-search the $-space.

    Returns a dict with keys
        accuracy, labels, gpu_hours, label_dollars, gpu_dollars
    or **None** if no feasible allocation meets the constraints.
    """
    budget = int(round(budget))
    best: Optional[Dict[str, float]] = None

    for lbl_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - lbl_dollars

        labels = lbl_dollars / label_cost if label_cost else 0.0
        gpu_hours = gpu_dollars / gpu_cost if gpu_cost else 0.0

        if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
            continue  # violates hard GPU cap

        acc_lbl = _eval_curve(curve_label["a"], curve_label["b"], labels)
        acc_gpu = _eval_curve(curve_gpu["a"], curve_gpu["b"], gpu_hours)
        acc = _combine(acc_lbl, acc_gpu)

        if best is None or acc > best["accuracy"]:
            best = {
                "accuracy": acc,
                "labels": labels,
                "gpu_hours": gpu_hours,
                "label_dollars": lbl_dollars,
                "gpu_dollars": gpu_dollars,
            }

    return best


# ───────────────────────────────────────────────────────── legacy alias ─────
# Keep the old name alive so unit tests or notebooks written earlier still run.
optimize_budget = optimise_budget  # type: ignore
