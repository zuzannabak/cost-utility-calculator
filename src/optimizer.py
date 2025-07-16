"""
Exhaustive search for the best split between labelling dollars
and GPU-compute dollars under a total-budget (and optional GPU-hour) cap.
"""

from typing import Dict, Optional

import numpy as np

# ---------------------------------------------------------------------------#
# Helpers                                                                    #
# ---------------------------------------------------------------------------#


def _eval_curve(a: float, b: float, x: float) -> float:
    """Saturating log curve  a · (1 − e^(−b·x))."""
    return a * (1.0 - np.exp(-b * x))


def _combine(acc_lbl: float, acc_gpu: float) -> float:
    """
    Combine two independent accuracy contributions.

    Using complement multiplication:
        1 − (1−acc_lbl)·(1−acc_gpu)
    """
    return 1.0 - (1.0 - acc_lbl) * (1.0 - acc_gpu)


# ---------------------------------------------------------------------------#
# Public API                                                                 #
# ---------------------------------------------------------------------------#


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
    Grid-search the $-space.

    Returns
    -------
    dict | None
        Best allocation dict with keys
            accuracy, labels, gpu_hours, label_dollars, gpu_dollars
        or *None* when no split satisfies the GPU-hour cap.
    """
    budget = int(round(budget))
    best: Optional[Dict[str, float]] = None

    for label_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - label_dollars

        labels = label_dollars / label_cost if label_cost else 0.0
        gpu_hours = gpu_dollars / gpu_cost if gpu_cost else 0.0

        if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
            continue

        acc = _combine(
            _eval_curve(curve_label["a"], curve_label["b"], labels),
            _eval_curve(curve_gpu["a"], curve_gpu["b"], gpu_hours),
        )

        if best is None or acc > best["accuracy"]:
            best = {
                "accuracy": acc,
                "labels": labels,
                "gpu_hours": gpu_hours,
                "label_dollars": label_dollars,
                "gpu_dollars": gpu_dollars,
            }

    return best


# ---------------------------------------------------------------------------#
# Backwards-compat alias (old notebooks)                                     #
# ---------------------------------------------------------------------------#

optimize_budget = optimise_budget  # type: ignore
