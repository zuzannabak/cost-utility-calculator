# src/cucal/cost_utils.py

from typing import Union

__all__ = [
    "as_hourly",
]


def as_hourly(cost: Union[int, float], inst_per_hour: int = 5) -> float:
    """Convert a *per‑instance* cost into an hourly cost.

    Parameters
    ----------
    cost : float | int
        Dollar cost for a **single** instance.
    inst_per_hour : int, default 5
        Throughput γ (instances processed per hour).

    Returns
    -------
    float
        Equivalent $/hour.
    """
    
    return float(cost) * inst_per_hour