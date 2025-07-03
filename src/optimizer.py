import numpy as np

def optimize_budget(label_cost, gpu_cost, budget, curve_params, granularity=5):
    """
    Sweep every `granularity` dollars and keep the best accuracy split.
    """
    budget = int(round(budget))
    best = {"accuracy": 0, "labels": 0, "gpu": 0}

    for lbl_dollars in range(0, budget + 1, granularity):
        gpu_dollars = budget - lbl_dollars
        labels = lbl_dollars / label_cost

        # simple log-curve accuracy
        acc = curve_params["a"] * (1 - np.exp(-curve_params["b"] * labels))

        if acc > best["accuracy"]:
            best.update({"accuracy": acc,
                         "labels": lbl_dollars,
                         "gpu": gpu_dollars})
    return best
