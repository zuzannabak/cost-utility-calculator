"""
Exhaustive search for the best split between labelling dollars
and GPU-compute dollars under a total-budget cap, an optional GPU-hour cap,
and an optional wall-clock-time limit (cluster efficiency taken into account).
"""

from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Dict, Optional, Union

import numpy as np
from src.api import k_resource


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
    curve_rmse: float = 0.02,               # NEW  ◀─────────────────────────
    max_gpu_hours: Optional[float] = None,
    wall_clock_limit_hours: Optional[float] = None,
    cluster_efficiency_pct: float = 60.0,
    granularity: int = 1,
) -> Optional[Dict[str, float]]:
    """
    Grid-search the $-space and return the best feasible split.

    Returned dict
    -------------
    accuracy          : mean value from the two curves
    accuracy_std      : 1 σ error (float)
    accuracy_ci       : (lo, hi) 95 % confidence interval
    labels            : number of human-labelled examples
    gpu_hours         : GPU compute hours purchased
    wall_clock_hours  : gpu_hours ÷ (cluster_efficiency_pct / 100)
    label_dollars     : dollars spent on annotation
    gpu_dollars       : dollars spent on compute
    """
    budget = int(round(budget))
    best: Optional[Dict[str, float]] = None

    efficiency = max(cluster_efficiency_pct, 1.0) / 100.0   # guard /0

    for label_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - label_dollars

        labels = label_dollars / label_cost if label_cost else 0.0
        gpu_hours = gpu_dollars / gpu_cost if gpu_cost else 0.0

        # 1️⃣  Hard GPU-hour cap
        if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
            continue

        # 2️⃣  Wall-clock constraint
        wall_clock = gpu_hours / efficiency
        if wall_clock_limit_hours is not None and wall_clock > wall_clock_limit_hours:
            continue

        # 3️⃣  Accumulate accuracy from the two curves
        acc = _combine(
            _eval_curve(curve_label["a"], curve_label["b"], labels),
            _eval_curve(curve_gpu["a"],  curve_gpu["b"],  gpu_hours),
        )

        # 4️⃣  Error model (task-level RMSE → σ)
        std = max(curve_rmse, 0.02)               # never let σ collapse to 0
        ci_lo = max(0.0, acc - 1.96 * std)
        ci_hi = min(1.0, acc + 1.96 * std)

        # 5️⃣  Keep the best solution
        if best is None or acc > best["accuracy"]:
            best = {
                "accuracy":         acc,
                "accuracy_std":     std,
                "accuracy_ci":      (ci_lo, ci_hi),
                "labels":           labels,
                "gpu_hours":        gpu_hours,
                "wall_clock_hours": wall_clock,
                "label_dollars":    label_dollars,
                "gpu_dollars":      gpu_dollars,
            }

    return best


# -----------------------------  Generic allocator  -------------------------#
def optimise_allocation(
    *,
    demand: float,
    resource_ids: Union[str, Sequence[str]],
    capacity_for: Callable[[str], float],
) -> AllocationPlan:
    """Allocate *demand* units across one or many resources at minimal cost."""
    if isinstance(resource_ids, str):
        resource_ids = [resource_ids]

    costs = k_resource.unit_costs(resource_ids)  # dict[str, float]

    remaining = demand
    alloc: dict[str, float] = {}

    for rid in sorted(resource_ids, key=costs.get):  # ascending $
        cap = capacity_for(rid)
        take = min(remaining, cap)
        alloc[rid] = take
        remaining -= take
        if remaining == 0:
            break

    if remaining:
        raise ValueError(
            f"Demand ({demand}) exceeds total capacity; {remaining} unfilled"
        )

    total_cost = sum(alloc[rid] * costs[rid] for rid in alloc)
    return AllocationPlan(per_resource=alloc, total_cost=total_cost)


# ---------------------------------------------------------------------------#
# Backwards-compat aliases                                                   #
# ---------------------------------------------------------------------------#
optimize_budget = optimise_budget  # type: ignore
optimise_budget_ci = optimise_budget
optimise_k_resource = optimise_allocation
