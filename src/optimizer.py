# src/optimizer.py
import math
from typing import Dict

def optimize_budget(label_cost, gpu_cost, budget, curve_params):
    """
    Grid-search best split of budget between labels and GPU.

    curve_params = {"a":…, "b":…}  from data/curves.json
    Returns dict {labels: $, gpu: $, accuracy: float}
    """
    a, b = curve_params["a"], curve_params["b"]
    best = {"labels": 0, "gpu": 0, "accuracy": 0.0}
    for lbl in range(0, budget+1, 5):            # $5 granularity
        gpu = budget - lbl
        ann_units = lbl / label_cost             # #labels
        dist_units = gpu / gpu_cost              # GPU-hours
        # simple combo: treat annotation minutes as x
        x = ann_units + dist_units
        acc = a * math.log(b * x + 1)
        acc = min(acc, 1.0)  
        if acc > best["accuracy"]:
            best = {"labels": lbl, "gpu": gpu, "accuracy": acc}
    return best
