"""Smoke tests for the budget optimiser."""

from src.optimizer import optimise_budget


def test_optimise_budget_dragut_smoke() -> None:
    """The optimiser should return a sane allocation dict."""
    label_curve = {"a": 0.73, "b": 0.48}
    gpu_curve = {"a": 0.69, "b": 0.44}

    res = optimise_budget(
        label_cost=0.05,
        gpu_cost=1.0,
        budget=100,
        curve_label=label_curve,
        curve_gpu=gpu_curve,
        max_gpu_hours=80,
        granularity=5,
    )

    assert res is not None, "No feasible allocation returned"
    assert 0.0 < res["accuracy"] <= 1.0
    assert res["label_dollars"] + res["gpu_dollars"] == 100
