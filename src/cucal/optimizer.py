from __future__ import annotations
"""
Exhaustive search for the best split between labelling dollars
and GPU-compute dollars under
* a total-budget cap,
* an optional GPU-hour cap, and
* an optional wall-clock-time limit (cluster-efficiency aware).
"""

from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Dict, Optional, Union

import numpy as np
from api import k_resource  # external dependency

from .config import DEFAULT_CLUSTER_EFF

# ---------------------------------------------------------------------------#
# Helper functions                                                           #
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
# Public dataclass for generic allocator                                     #
# ---------------------------------------------------------------------------#
@dataclass(slots=True)
class AllocationPlan:
    per_resource: dict[str, float]  # id → units allocated
    total_cost: float


# ---------------------------------------------------------------------------#
# Budget-split optimiser                                                     #
# ---------------------------------------------------------------------------#
def optimise_budget(
    *,
    label_cost: float,          # $ per **instance**
    gpu_cost: float,
    budget: float,
    curve_label: Dict[str, float],
    curve_gpu: Dict[str, float],
    label_rmse: float = 0.0,   # passed in from GUI (label curve)
    gamma: int = 5,
    max_gpu_hours: Optional[float] = None,
    wall_clock_limit_hours: Optional[float] = None,
    cluster_efficiency_pct: float = 100 * DEFAULT_CLUSTER_EFF,
    granularity: int = 1,
    target_accuracy: float | None = None,   # NEW
) -> Optional[Dict[str, float]]:
    """
    Grid-search the $-space.

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
    assert gamma > 0, "γ must be > 0"
    budget = int(round(budget))
    best: Optional[Dict[str, float]] = None
    efficiency = max(cluster_efficiency_pct, 1.0) / 100.0  # avoid /0

    # -----------------------------------------------------------------------
    # Grid-search     label_dollars ∈ [0 … budget]
    #                 gpu_dollars   ∈ [0 … budget − label_dollars]
    # -----------------------------------------------------------------------
    for label_dollars in range(0, budget + 1, granularity):
        for gpu_dollars in range(0, budget - label_dollars + 1, granularity):

            spent = label_dollars + gpu_dollars            # NEW — total $

            # ---------- convert dollars → units --------------------------------
            labels = label_dollars / label_cost
            label_hours = labels / gamma
            gpu_hours = gpu_dollars / gpu_cost if gpu_cost else 0.0

            # ---------- caps ----------------------------------------------------
            if max_gpu_hours is not None and gpu_hours > max_gpu_hours:
                continue

            wall_clock = gpu_hours / efficiency + label_hours
            if (
                wall_clock_limit_hours is not None
                and wall_clock > wall_clock_limit_hours
            ):
                continue

            # ---------- accuracy ------------------------------------------------
            acc = _combine(
                _eval_curve(curve_label["a"], curve_label["b"], labels),
                _eval_curve(curve_gpu["a"], curve_gpu["b"], gpu_hours),
            )

            # ---------- pick “better” plan --------------------------------------
            if target_accuracy is None:                         # maximise acc
                better = (
                    best is None
                    or acc > best["accuracy"]
                    or (acc == best["accuracy"] and spent > best["spent"])
                )
            else:                                               # hit target
                meets_target = acc >= target_accuracy
                better = (
                    meets_target
                    and (best is None or spent < best["spent"])
                )

            if not better:
                continue

            # ---------- confidence interval -------------------------------------
            rmse = (label_rmse**2 + curve_gpu.get("rmse", 0.0) ** 2) ** 0.5
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
                "spent": spent,                     # <- tie-break helper
            }

    return best


# ---------------------------------------------------------------------------#
# Generic k-resource allocator (unchanged, but imported by other modules)    #
# ---------------------------------------------------------------------------#
def optimise_allocation(
    *,
    demand: float,
    resource_ids: Union[str, Sequence[str]],
    capacity_for: Callable[[str], float],
) -> AllocationPlan:
    """
    Allocate *demand* units across one or many resources at minimal total cost.
    """
    if isinstance(resource_ids, str):
        resource_ids = [resource_ids]

    # Unit-mismatch guard
    if hasattr(k_resource, "meta"):
        target_unit = k_resource.meta(resource_ids[0])["unit"]
        for rid in resource_ids:
            assert k_resource.meta(rid)["unit"] == target_unit, (
                f"Unit mismatch: {rid} is in {k_resource.meta(rid)['unit']}, "
                f"expected {target_unit}."
            )

    costs = k_resource.unit_costs(resource_ids)  # {rid: $/unit}
    remaining = demand
    alloc: dict[str, float] = {}

    for rid in sorted(resource_ids, key=costs.get):  # cheapest first
        cap = capacity_for(rid)
        take = min(remaining, cap)
        alloc[rid] = take
        remaining -= take
        if remaining == 0:
            break

    if remaining:
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
