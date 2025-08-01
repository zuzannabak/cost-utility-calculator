#!/usr/bin/env python3
"""Wylicz minimalny koszt vs. η i narysuj heat-mapę lub wykres liniowy."""

import os
import numpy as np
import matplotlib.pyplot as plt

from cucal.curves    import get_curves          # ← Twój helper
from cucal.optimizer import optimise_budget     # ← główny optymalizator

# --------------------------------------------------  parametry
target_f1      = 0.83
label_cost     = 0.05          # $ za jedną etykietę (przykład)
base_gpu_cost  = 1.00          # $ za 1 GPU-h przy η = 1
t_max_hours    = 24

etas = np.linspace(0.5, 1.0, 11)   # 0.50, 0.55, …, 1.00
min_costs = []

# wczytaj krzywe (zmień 'Dragut-2019' na właściwy zestaw)
curve_lbl, curve_gpu = get_curves("Dragut-2019")

# --------------------------------------------------  pętla po η
for eta in etas:
    gpu_cost = base_gpu_cost / eta

    # szukamy najmniejszego budżetu, który osiąga target_F1
    best_cost = None
    for budget in range(50, 601, 10):          # sweep 50 $ → 600 $
        res = optimise_budget(
            label_cost=label_cost,
            gpu_cost=gpu_cost,
            budget=budget,
            curve_label=curve_lbl,
            curve_gpu=curve_gpu,
            target_accuracy=target_f1,
            max_gpu_hours=t_max_hours,
        )
        if res is not None:                    # mamy plan spełniający F1
            best_cost = res["label_dollars"] + res["gpu_dollars"]
            break                              # to już minimalny koszt

    min_costs.append(best_cost if best_cost is not None else np.nan)

# --------------------------------------------------  rysunek  (WERSJA LINIIOWA — czytelniejsza)
fig, ax = plt.subplots(figsize=(5, 3))
ax.plot(etas, min_costs, marker="o")
ax.set_xlabel(r"Cluster efficiency $\eta$")
ax.set_ylabel("Minimal cost ($)")
ax.set_title(f"Sensitivity of cost (F1 ≥ {target_f1})")

fig.tight_layout()
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/eta_vs_cost.png", dpi=300)

# --------------------------------------------------  (Opcjonalnie) heat-mapa 1×N — analogicznie do wcześniejszej
# ...
