# scripts/make_heatmap.py
import numpy as np, matplotlib.pyplot as plt
etas  = np.linspace(0.5,1.0,11)
costs = 310 * (0.9/etas)          # toy formula, replace with real values
plt.imshow(costs.reshape(1,-1), aspect='auto', cmap='plasma',
           extent=[0.5,1.0,0,1])
plt.yticks([]); plt.xlabel(r"Cluster efficiency $\eta$")
plt.colorbar(label="Min cost ($)")
plt.savefig("figures/heatmap_eff.png")
