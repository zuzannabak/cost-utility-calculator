# src/cucal/model_types.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(slots=True)
class ResourceCurve:
    """
    One cost/accuracy curve for a given resource (dataset, GPU, etc.)
    """
    name: str
    curve: Dict[str, float]          # e.g. {"a": 0.72, "b": -0.03}
    cost_per_unit: float             # $ per label or GPU-hour
    max_units: Optional[int] = None  # cap (None → unlimited)


@dataclass(slots=True)
class AllocationPlan:
    per_resource: Dict[str, float]  # id → units
    total_cost: float
    accuracy: float


@dataclass(slots=True)
class Resource:
    """Cost‑bearing resource in the optimisation model."""
    name: str
    unit: str        # "inst", "gpu-h", "dev-h", …
    cost_per_unit: float