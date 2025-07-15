# ── src/optimizer.py ───────────────────────────────────────────
from typing import Dict

import numpy as np


def optimize_budget(
    label_cost: float,
    gpu_cost: float,
    budget: float,
    curve_params: Dict[str, float],
    granularity: int = 5,
) -> dict:
    """
    Exhaustive $-split search across label $ and GPU $.
    """
    budget = int(round(budget))
    best = {"accuracy": 0, "labels": 0, "gpu": 0}

    for lbl_dollars in range(0, budget  1, granularity):
        gpu_dollars = budget - lbl_dollars
        labels = lbl_dollars / label_cost

        # gpu_hours = gpu_dollars / gpu_cost  reserved for future use

        acc = curve_params["a"] * (1 - np.exp(-curve_params["b"] * labels))

        if acc > best["accuracy"]:
            best.update({"accuracy": acc, "labels": lbl_dollars, "gpu": gpu_dollars})
    return best

def _eval_curve(a: float, b: float, x: float) -> float:
    """Generic saturating-log curve used for both labels and GPU-hours."""
    return a * (1 - np.exp(-b * x))


def _combine(acc_label: float, acc_gpu: float) -> float:
    """
    Heuristic joint accuracy: 1 – (1–a)(1–b)  (complements multiply).
    Feel free to swap in a different rule later.
    """
    return 1 - (1 - acc_label) * (1 - acc_gpu)


def optimise_budget(  # NOTE British spelling = new public name
    *,
    label_cost: float,
    gpu_cost: float,
    budget: float,
    curve_label: Dict[str, float],
    curve_gpu: Dict[str, float],
    max_gpu_hours: Optional[float] = None,
    granularity: int = 5,
) -> Dict[str, float]:
    """
    Exhaustive search over how to split **money** between labelling and GPU-time.

    Returns a dict with keys:
        accuracy, labels, gpu_hours, label_dollars, gpu_dollars
    """
    budget = int(round(budget))
    best: Dict[str, float] = {"accuracy": 0.0}

    # Search on $1 (or `granularity`) grid
    for lbl_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - lbl_dollars

        labels = lbl_dollars / label_cost
        gpu_hours = gpu_dollars / gpu_cost

        if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
            continue  # violates the constraint

        acc_lbl = _eval_curve(curve_label["a"], curve_label["b"], labels)
        acc_gpu = _eval_curve(curve_gpu["a"], curve_gpu["b"], gpu_hours)
        acc = _combine(acc_lbl, acc_gpu)

        if acc > best["accuracy"]:
            best = {
                "accuracy": acc,
                "labels": labels,
                "gpu_hours": gpu_hours,
                "label_dollars": lbl_dollars,
                "gpu_dollars": gpu_dollars,
            }
    return best