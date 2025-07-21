"""
Exhaustive search for the best split between labelling dollars
and GPU-compute dollars under a total-budget (and optional GPU-hour) cap.
"""

from __future__ import annotations  # if you’re on Python < 3.11

from collections.abc import Sequence
from dataclasses import dataclass

from typing import Union

from src.api import k_resource

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
@dataclass(slots=True)
class AllocationPlan:
    per_resource: dict[str, float]  # id → units allocated
    total_cost: float


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


def optimise_allocation(
    *,
    demand: float,
    resource_ids: Union[str, Sequence[str]],
    capacity_for,  # ← pass a callable so the fn stays generic
) -> AllocationPlan:
    """
    Allocate *demand* units across one or many resources at minimal total cost.

    Parameters
    ----------
    demand : float
        Units required (e.g. GPU-hours, documents, whatever).
    resource_ids : str | Sequence[str]
        One ID or an iterable of IDs.
    capacity_for : Callable[[str], float]
        User-supplied function that returns the capacity of a given resource ID.

    Returns
    -------
    AllocationPlan
    """
    # 1  Normalise the input to a list
    if isinstance(resource_ids, str):
        resource_ids = [resource_ids]

    # 2  Bulk-fetch unit prices
    costs = k_resource.unit_costs(resource_ids)  # dict[str, float]

    # 3  Greedy cheapest-first allocation
    remaining = demand
    alloc: dict[str, float] = {}

    for rid in sorted(resource_ids, key=costs.get):  # ascending $
        cap = capacity_for(rid)
        take = min(remaining, cap)
        alloc[rid] = take
        remaining -= take
        if remaining == 0:
            break

    if remaining:  # unmet demand
        raise ValueError(
            f"Demand ({demand}) exceeds total capacity; {remaining} left unfilled"
        )

    total_cost = sum(alloc[rid] * costs[rid] for rid in alloc)
    return AllocationPlan(per_resource=alloc, total_cost=total_cost)


# ---------------------------------------------------------------------------#
# Backwards-compat alias (old notebooks)                                     #
# ---------------------------------------------------------------------------#

optimize_budget = optimise_budget  # type: ignore
optimise_k_resource = optimise_allocation  # backwards-compat alias
