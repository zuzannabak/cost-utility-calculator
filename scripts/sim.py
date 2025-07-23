#!/usr/bin/env python3
"""
Command-line wrapper around cucal.optimizer.optimise_budget

Examples
--------
# Dragut demo with a $1 500 budget
python sim.py Dragut-2019 --budget 1500

# If you really want to pass explicit keys:
python sim.py Dragut-2019 --label-key Dragut-2019-label --gpu-key Dragut-2019-gpu
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

# make “cucal” importable when running as a standalone script
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cucal.optimizer import optimise_budget


# ---------------------------------------------------------------------------#
# Helpers
# ---------------------------------------------------------------------------#
def load_curves(label_key: str, gpu_key: str):
    curves = json.loads((ROOT / "data" / "curves.json").read_text())
    try:
        lbl_entry = curves[label_key]["label_curve"]
        gpu_entry = curves[gpu_key]["gpu_curve"]
    except KeyError as e:
        raise SystemExit(f"Key {e} not found in curves.json") from None
    return lbl_entry, gpu_entry


# ---------------------------------------------------------------------------#
# CLI
# ---------------------------------------------------------------------------#
def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "task",
        help='Base name, e.g. "Dragut-2019", "Kang-2023", '
        'or "Stiennon2021" (no -label / -gpu suffix)',
    )
    p.add_argument("--budget", type=float, required=True, help="Total $ budget")
    p.add_argument("--label-cost", type=float, default=0.10)
    p.add_argument("--gpu-cost", type=float, default=3.00)

    # power-user overrides
    p.add_argument("--label-key", help="Override label resource key")
    p.add_argument("--gpu-key", help="Override GPU resource key")
    args = p.parse_args(argv)

    label_key = args.label_key or f"{args.task}-label"
    gpu_key = args.gpu_key or f"{args.task}-gpu"

    curve_lbl, curve_gpu = load_curves(label_key, gpu_key)

    result = optimise_budget(
        label_cost=args.label_cost,
        gpu_cost=args.gpu_cost,
        budget=args.budget,
        curve_label=curve_lbl,
        curve_gpu=curve_gpu,
    )

    print(f"\n=== Optimal split for {args.task} on ${args.budget:.0f} ===")
    print(f"Label dollars : {result['label_dollars']:8.2f}")
    print(f"GPU dollars   : {result['gpu_dollars']:8.2f}")
    print(f"Expected accuracy ≈ {result['accuracy']:.3f}")


if __name__ == "__main__":  # pragma: no cover
    main()
