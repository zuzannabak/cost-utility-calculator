
from __future__ import annotations
"""
Exhaustive search for the best split between labelling dollars
and GPU-compute dollars under a total-budget cap, an optional GPU-hour cap,
and an optional wall-clock-time limit (cluster efficiency taken into account).
"""

from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Dict, Optional, Union
from cucal.cost_utils import as_hourly

import numpy as np
from src.api import k_resource  # external dependency

# ---------------------------------------------------------------------------#
# Helpers                                                                    #
# ---------------------------------------------------------------------------#


def _eval_curve(a: float, b: float, x: float) -> float:
    """Saturating log curve  a · (1 − e^(−b·x))."""
    return a * (1.0 - np.exp(-b * x))


def _combine(acc_lbl: float, acc_gpu: float) -> float:
    """
    Combine two independent accuracy contributions using complement
    multiplication:  1 − (1−acc_lbl)·(1−acc_gpu)
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
    gamma: int = 5,
    max_gpu_hours: Optional[float] = None,
    wall_clock_limit_hours: Optional[float] = None,
    cluster_efficiency_pct: float = 60.0,
    granularity: int = 1,
) -> Optional[Dict[str, float]]:
    """
    Grid-search the $-space.

    Parameters
    ----------
    label_cost : float
        $ cost per labelled example.
    gpu_cost : float
        $ cost per GPU-hour.
    budget : float
        Total dollars available.
    curve_label / curve_gpu : dict
        Keys {a, b [, rmse]} for the two accuracy curves.
    max_gpu_hours : float | None
        Hard cap on GPU hours (wall-clock × #GPUs). None → unlimited.
    wall_clock_limit_hours : float | None
        If set, prune any candidate whose estimated wall-clock time
        ( gpu_hours / (cluster_efficiency_pct/100) )
        exceeds this limit.
    cluster_efficiency_pct : float
        Aggregate utilisation + scheduling efficiency, 10–100 %.
    granularity : int
        Dollar step size for the grid search.

    Returns
    -------
    dict | None
        {
          accuracy, accuracy_ci,
          labels, gpu_hours,
          wall_clock_hours,
          label_dollars, gpu_dollars
        }
        or *None* when no split satisfies the caps.
    """
    assert gamma > 0, "γ must be > 0"
    budget = int(round(budget))
    best: Optional[Dict[str, float]] = None
    efficiency = max(cluster_efficiency_pct, 1.0) / 100.0  # avoid /0

    for label_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - label_dollars

        # convert per‑instance $ to per‑hour $ so we *could* estimate
        # labelling wall‑clock later (unused for now)
        hourly_label_cost = as_hourly(label_cost, gamma)

        labels = label_dollars / label_cost           # examples labelled
        label_hours = label_dollars / hourly_label_cost  # hours spent labelling

        gpu_hours = gpu_dollars / gpu_cost if gpu_cost else 0.0

        if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
            continue

        # Only GPU time counts toward wall‑clock for now; add label_hours
        wall_clock = gpu_hours / efficiency if efficiency else float("inf")
        if wall_clock_limit_hours is not None and wall_clock > wall_clock_limit_hours:
            continue

        acc = _combine(
            _eval_curve(curve_label["a"], curve_label["b"], labels),
            _eval_curve(curve_gpu["a"], curve_gpu["b"], gpu_hours),
        )

        if best is None or acc > best["accuracy"]:
            rmse = curve_label.get("rmse", 0.0)
            ci_lo = max(0.0, acc - 1.96 * rmse)
            ci_hi = min(1.0, acc + 1.96 * rmse)
            best = {
                "accuracy": acc,
                "accuracy_ci": (ci_lo, ci_hi),
                "labels": labels,
                "gpu_hours": gpu_hours,
                "wall_clock_hours": wall_clock,
                "label_dollars": label_dollars,
                "gpu_dollars": gpu_dollars,
            }

    return best


# -----------------------------  Generic allocator  -------------------------#
def optimise_allocation(
    *,
    demand: float,
    resource_ids: Union[str, Sequence[str]],
    capacity_for: Callable[[str], float],
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
        Function returning the capacity of a given resource ID.

    Returns
    -------
    AllocationPlan
    """

    if isinstance(resource_ids, str):
        resource_ids = [resource_ids]

    # ---  UNIT‑MISMATCH GUARD  -------------------------------------
    # Verify every candidate resource uses the same unit. Prevents bugs
    # where, e.g., a "gpu-h" pool gets compared with a "node-h" pool.

    target_unit = k_resource.meta(resource_ids[0])["unit"]
    for rid in resource_ids:
        assert k_resource.meta(rid)["unit"] == target_unit, (
            f"Unit mismatch: {rid} is in {k_resource.meta(rid)['unit']}, "
            f"expected {target_unit}."
        )

    # Bulk‑fetch unit prices (safe now that units match)
    costs = k_resource.unit_costs(resource_ids)  # dict[str, float]

    # Greedy cheapest-first allocation
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
# Backwards-compat aliases (notebooks, legacy code)                          #
# ---------------------------------------------------------------------------#

optimize_budget = optimise_budget  # type: ignore


def optimise_budget_ci(*args, **kwargs):
    return optimise_budget(*args, **kwargs)


optimise_k_resource = optimise_allocation
