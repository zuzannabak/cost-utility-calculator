#!/usr/bin/env python3
"""
CLI wrapper for optimize_budget.
Usage: python sim.py Dragut-2019-label 100
"""
import json, argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from cucal.optimizer import optimize_budget

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("curve",  help="Name in curves.json (Dragut-2019-label, Kang2023, …)")
    ap.add_argument("budget", type=float, help="Total $ budget")
    ap.add_argument("--label_cost", type=float, default=0.10)
    ap.add_argument("--gpu_cost",   type=float, default=3.0)
    args = ap.parse_args()

    curves = json.load(open(pathlib.Path("data/curves.json")))
    if args.curve not in curves:
        raise SystemExit(f"Curve {args.curve} not found in data/curves.json")

    a,b = curves[args.curve]["a"], curves[args.curve]["b"]
    result = optimize_budget(args.label_cost, args.gpu_cost, args.budget, {"a":a,"b":b})

    print(f"\n=== Optimal split for {args.curve} on ${args.budget:.0f} ===")
    print(f"Labels: ${result['labels']:.2f}  │  GPU: ${result['gpu']:.2f}")
    print(f"Expected accuracy ≈ {result['accuracy']:.3f}")

if __name__ == "__main__":
    main()
