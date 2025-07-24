"""
CLI entry-point so you can call `python -m cucal ...`.
"""

import argparse
from cucal.optimizer import optimise_budget
from cucal.curves import get_curves
from cucal.config import DEFAULT_CLUSTER_EFF


def main() -> None:
    ap = argparse.ArgumentParser(description="Cost-Utility optimiser")
    ap.add_argument("--budget", type=float, required=True, help="Total $ budget")
    ap.add_argument("--time", type=float, help="Wall-clock limit (h)")
    ap.add_argument("--eff", type=float, default=100 * DEFAULT_CLUSTER_EFF,
                    help="Cluster efficiency (percent, default 90)")
    ap.add_argument("--gpu_cap", type=float, help="Max GPU-h")
    ap.add_argument("--label_cost", type=float, default=0.1)
    ap.add_argument("--gpu_cost", type=float, default=3.0)
    ap.add_argument("case", help="Case-study name, e.g. Dragut2019")
    args = ap.parse_args()

    curve_lbl, curve_gpu = get_curves(args.case)
    plan = optimise_budget(
        label_cost=args.label_cost,
        gpu_cost=args.gpu_cost,
        budget=args.budget,
        curve_label=curve_lbl,
        curve_gpu=curve_gpu,
        max_gpu_hours=args.gpu_cap,
        wall_clock_limit_hours=args.time,
        cluster_efficiency_pct=args.eff,
    )
    print(plan if plan else "No feasible plan.")


if __name__ == "__main__":
    main()
