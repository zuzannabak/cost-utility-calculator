from src.optimizer import optimise_budget

DUMMY = {"a": 1.0, "b": 0.001, "rmse": 0.0}


def test_within_time_budget():
    sol = optimise_budget(
        label_cost=1.0,
        gpu_cost=1.0,
        budget=1000.0,
        curve_label=DUMMY,
        curve_gpu=DUMMY,
        wall_clock_limit_hours=72,
    )
    assert sol["wall_clock_hours"] <= 72


def test_no_feasible_split():
    sol = optimise_budget(
        label_cost=1.0,
        gpu_cost=1.0,
        budget=1000.0,
        curve_label=DUMMY,
        curve_gpu=DUMMY,
        wall_clock_limit_hours=0.1,
    )
    # A plan is feasible only if wall-clock ≤ cap
    assert sol is None or sol["wall_clock_hours"] <= 0.1
