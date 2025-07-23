#!/usr/bin/env python3
"""
Validate the simulator against Dragut-2019 numbers.

Usage:
    python scripts/validate_dragut.py --budget 1500 --time 24
or
    python -m cucal.validate dragut  (added in step-2)
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

from cucal.optimizer import optimise_budget           # <- k-resource API


# ------------------------- helpers ------------------------- #
PAPER_ACCURACY = 0.785      # Dragut-2019 F1   (edit!)
THRESHOLD     = 0.005       # 0.5 percentage-point


def _run_validation(budget: float, time_cap: float, eff: float) -> None:
    root = Path(__file__).resolve().parents[1]          # repo root
    curves = json.loads((root / "data" / "curves.json").read_text())

    label_entry = curves["Dragut-2019-label"]
    gpu_entry   = curves["Dragut-2019-gpu"]

    result = optimise_budget(
        label_cost=label_entry["cost_per_unit"],
        gpu_cost=gpu_entry["cost_per_unit"],
        budget=budget,
        curve_label=label_entry["label_curve"],
        curve_gpu=gpu_entry["gpu_curve"],
        wall_clock_limit_hours=time_cap,
        cluster_efficiency_pct=eff * 100,
    )

    sim_acc = result["accuracy"]
    delta   = abs(sim_acc - PAPER_ACCURACY)

    print("\nDragut-2019 validation\n" + "-"*28)
    print(f"Paper accuracy : {PAPER_ACCURACY:.3f}")
    print(f"Simulator acc. : {sim_acc:.3f}")
    print(f"Delta accuracy     : {delta:.3%}")
    print("\nRecommended split ($):")
    print(f"  label_dollars   {result['label_dollars']:8.2f}")
    print(f"  gpu_dollars     {result['gpu_dollars']:8.2f}")

    # hard assertion for CI
    assert delta < THRESHOLD, (
        f"Validation failed: Delta {delta:.3%} exceeds {THRESHOLD:.3%}"
    )


# ------------------------- CLI ------------------------- #
def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=float, default=1500, help="Total budget in $")
    p.add_argument("--time",   type=float, default=24,   help="Max wall-clock hours")
    p.add_argument("--eff",    type=float, default=1.0,  help="Cluster efficiency 0–1")
    args = p.parse_args(argv)
    _run_validation(args.budget, args.time, args.eff)


if __name__ == "__main__":   # pragma: no cover
    main()
