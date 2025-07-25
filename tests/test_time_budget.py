"""
Unit-test: optimise_budget must never return a plan whose wall-clock time
exceeds the user-supplied limit.
"""

from cucal.optimizer import optimise_budget


def test_respects_wall_clock_limit() -> None:
    """
    With a $10 budget, $2 per GPU-hour, the worst-case GPU time is 5 h.
    We pass a 5-hour wall-clock limit, so the function *must* return
    a plan and that plan must fit the cap.
    """
    plan = optimise_budget(
        label_cost=1.0,                  # $ per labelled example (cheap)
        gpu_cost=2.0,                    # $ per GPU-hour
        budget=10.0,                     # total $
        curve_label={"a": 1.0, "b": 0.1},
        curve_gpu={"a": 1.0, "b": 0.1},
        wall_clock_limit_hours=5.0,      # the constraint we want to test
        cluster_efficiency_pct=100,      # 100 % efficiency → wall-clock = GPU-h
        granularity=1,
    )

    # The optimiser should find a feasible split;
    # if none exists it would return None.
    assert plan is not None, "No feasible plan found despite sufficient budget"

    # And that plan must respect the limit.
    assert plan["wall_clock_hours"] <= 5.0, plan
