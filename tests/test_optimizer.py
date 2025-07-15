from src.optimizer import optimize_budget


def test_optimizer_budget_respected():
    params = {"a": 0.9, "b": 0.02}
    out = optimize_budget(label_cost=0.10, gpu_cost=3, budget=100, curve_params=params)
    assert out["labels"] + out["gpu"] <= 100
    assert 0 <= out["accuracy"] <= 1


def test_budget_split():
    out = optimize_budget(0.1, 3, 100, {"a": 0.6, "b": 0.05})
    assert out["labels"] + out["gpu"] == 100
    assert 0 <= out["accuracy"] <= 1

def test_optimise_budget_dragut_smoke():
    lbl_curve = {"a": 0.73, "b": 0.48}
    gpu_curve = {"a": 0.69, "b": 0.44}

    res = optimiser.optimise_budget(
        label_cost=0.05,
        gpu_cost=1.0,
        budget=100,
        curve_label=lbl_curve,
        curve_gpu=gpu_curve,
        max_gpu_hours=80,
        granularity=5,
    )
    assert 0 < res["accuracy"] <= 1
    assert res["label_dollars"] + res["gpu_dollars"] == 100