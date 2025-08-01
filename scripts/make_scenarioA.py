# scripts/make_scenarioA.py
#!/usr/bin/env python3
"""Bar chart: CUCal allocation + F1 for Scenario A."""

import os
import matplotlib.pyplot as plt

# --------------------------------------------------  dane
label_cost = 60
gpu_cost   = 340
f1         = 0.84

# --------------------------------------------------  rysunek
fig, ax_cost = plt.subplots()

bars = ax_cost.bar(['Labels', 'GPU'],
                   [label_cost, gpu_cost],
                   color=['#4C72B0', '#55A868'])
ax_cost.set_ylabel("Budget allocation ($)")

# etykiety nad słupkami
for bar in bars:
    height = bar.get_height()
    ax_cost.annotate(f"${height}",
                     xy=(bar.get_x() + bar.get_width()/2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9)

# druga oś — F1
ax_f1 = ax_cost.twinx()
ax_f1.axhline(f1, linestyle="--", color="grey", linewidth=1.5)
ax_f1.set_ylim(0.75, 0.90)                 # margines u góry/dole
ax_f1.set_ylabel("Accuracy (F1)")

# podpis linii F1
ax_f1.text(0.5, f1 + 0.005, f"F1 = {f1:.2f}",
           transform=ax_f1.get_xaxis_transform(),
           ha='center', va='bottom', color='grey')

fig.tight_layout()

# --------------------------------------------------  zapis
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/scenarioA.png", dpi=300)
