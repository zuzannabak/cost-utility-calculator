import json, pathlib, numpy as np

p = pathlib.Path("data/curves.json")
curves = json.loads(p.read_text())

a_med = float(np.median([v["label_curve"]["a"] for v in curves.values()]))
b_med = float(np.median([v["label_curve"]["b"] for v in curves.values()]))
g_med = float(np.median([v["gpu_curve"]["b"]   for v in curves.values()]))
curves["GenericNLP"] = {
    "label_curve": {"a": a_med, "b": b_med},
    "gpu_curve":   {"a": a_med * 0.96, "b": g_med},
}
p.write_text(json.dumps(curves, indent=2))
print("✅ Added GenericNLP curve")
