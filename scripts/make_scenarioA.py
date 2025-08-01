# scripts/make_scenarioA.py
import matplotlib.pyplot as plt
plt.bar(["Labels","GPU"], [60,340])
plt.twinx(); plt.plot([0,1], [0.84,0.84], marker='o')
plt.ylabel("Accuracy (F1)")
plt.savefig("figures/scenarioA.png")
