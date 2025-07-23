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

from src.cucal.optimizer import optimise_budget           # <- k-resource API
from src.cucal.model_types import ResourceCurve                 # <- dataclass in src/types.py


# ------------------------- helpers ------------------------- #
PAPER_ACCURACY = 0.785      # Dragut-2019 F1   (edit!)
THRESHOLD     = 0.005       # 0.5 percentage-point


def _load_dragut_curves(curves_path: Path) -> list[ResourceCurve]:
    with curves_path.open() as f:
        curves = json.load(f)

    curves_for_dragut = []
    for name, entry in curves.items():
        if name.startswith("Dragut-2019"):
            curves_for_dragut.append(
                ResourceCurve(
                    name=name,
                    curve=entry["label_curve"],         # ← your schema
                    cost_per_unit=entry["cost_per_unit"],
                    max_units=entry.get("max_units"),
                )
            )
    return curves_for_dragut


def _run_validation(budget: float, time_cap: float, eff: float) -> None:
    root = Path(__file__).resolve().parents[1]        # repo root
    curves_path = root / "data" / "curves.json"
    resources   = _load_dragut_curves(curves_path)

    result      = optimise_budget(
        resources,
        total_budget=budget,
        time_cap=time_cap,
        efficiency=eff,
    )

    sim_acc = result["accuracy"]
    delta   = abs(sim_acc - PAPER_ACCURACY)

    print("\nDragut-2019 validation\n" + "-"*28)
    print(f"Paper accuracy : {PAPER_ACCURACY:.3f}")
    print(f"Simulator acc. : {sim_acc:.3f}")
    print(f"Δ accuracy     : {delta:.3%}")
    print("\nRecommended split ($):")
    for k, v in result["split"].items():
        print(f"  {k:<15} {v:8.2f}")

    # hard assertion for CI
    assert delta < THRESHOLD, (
        f"Validation failed: Δ accuracy {delta:.3%} exceeds {THRESHOLD:.3%}"
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
