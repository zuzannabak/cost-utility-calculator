import pandas as pd, numpy as np, json, argparse
from pathlib import Path
from scipy.optimize import curve_fit

def sat(x, a, b):     # saturating log curve
    return a * (1 - np.exp(-b * x))

cli = argparse.ArgumentParser()
cli.add_argument("--csv", required=True)
cli.add_argument("--task", required=True)
cli.add_argument("--curve-type", choices=["label", "gpu"], required=True)
args = cli.parse_args()

df = pd.read_csv(args.csv)
x = df.iloc[:, 0].to_numpy()   # first column = x
y = df.iloc[:, 1].to_numpy()   # second column = y

(a, b), _ = curve_fit(sat, x, y, p0=(0.8, 0.0005), maxfev=10000)

curves_p = Path("data/curves.json")
curves = json.loads(curves_p.read_text())
curves.setdefault(args.task, {})[f"{args.curve_type}_curve"] = {
    "a": float(a),
    "b": float(b),
}
curves_p.write_text(json.dumps(curves, indent=2))
print(f"✅ wrote {args.curve_type} curve for {args.task}: a={a:.4f}, b={b:.6f}")
