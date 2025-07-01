# ── src/optimizer.py ───────────────────────────────────────────
import numpy as np
from typing import Dict

def optimize_budget(label_cost: float,
                    gpu_cost: float,
                    budget: float,
                    curve_params: Dict[str, float],
                    granularity: int = 5) -> dict:
    """
    Exhaustive $-split search across label $ and GPU $.
    """
    budget = int(round(budget))
    best   = {"accuracy": 0, "labels": 0, "gpu": 0}

    for lbl_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - lbl_dollars
        labels      = lbl_dollars / label_cost
        gpu_hours   = gpu_dollars / gpu_cost          # reserved for future use

        
        acc = curve_params["a"] * (1 - np.exp(-curve_params["b"] * labels))

        if acc > best["accuracy"]:
            best.update({"accuracy": acc,
                         "labels":   lbl_dollars,
                         "gpu":      gpu_dollars})
    return best
