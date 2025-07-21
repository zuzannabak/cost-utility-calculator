from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class AllocationPlan:
    per_resource: Dict[str, float]  # id → units (labels, gpu-hours, …)
    total_cost: float
    accuracy: float
