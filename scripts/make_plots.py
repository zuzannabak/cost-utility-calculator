# scripts/make_plots.py  (updated snippet)
import json, numpy as np, matplotlib.pyplot as plt
from pathlib import Path

CURVES = json.loads(Path("data/curves.json").read_text())
lbl = CURVES["Dragut-2019-label"]["label_curve"]
gpu = CURVES["Dragut-2019-gpu"]["gpu_curve"]

u = lambda a, b, x: a * (1 - np.exp(-b * x))

# horizontal axis in *dollars*
dollars = np.linspace(0, 1500, 200)
instances   = dollars / 0.02          # 2 c/inst
gpu_hours   = dollars / 1.40          # 1.4 $/h

plt.figure()
plt.plot(dollars, u(**lbl, x=instances), label="Labels ($0.02/inst$)")
plt.plot(dollars, u(**gpu, x=gpu_hours), label="GPU ($1.40/h$)")
plt.xlabel("Spend (US $)")
plt.ylabel("Utility (F1)")
plt.legend()
plt.tight_layout()
Path("figures").mkdir(exist_ok=True)
plt.savefig("figures/dragut_curves.pdf")
