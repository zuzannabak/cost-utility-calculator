# src/optimizer.py
import numpy as np
import math
from typing import Dict

def optimize_budget(label_cost: float,
                    gpu_cost: float,
                    budget: float,
                    curve_params: dict,
                    granularity=5) -> dict:
    """
    Exhaustive $ split search.
    """
    budget = int(round(budget))          # ← NEW: ensure integer dollars
    best   = {"accuracy": 0, "labels": 0, "gpu": 0}

    # $5-granularity sweep
    for lbl_dollars in range(0, int(budget)+1, granularity):
        gpu_dollars   = budget - lbl_dollars
        labels        = lbl_dollars / label_cost
        # gpu_hours reserved for energy-cost extension
        gpu_hours     = gpu_dollars / gpu_cost
        acc = curve["a"] * (1 - np.exp(-curve["b"] * labels))

        if acc > best["accuracy"]:
            best.update({"accuracy": acc,
                         "labels": lbl_dollars,
                         "gpu": gpu_dollars})
    return best

