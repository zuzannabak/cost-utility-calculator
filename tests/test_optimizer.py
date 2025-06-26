from src.optimizer import optimize_budget

def test_optimizer_budget_respected():
    params = {"a": 0.9, "b": 0.02}
    out = optimize_budget(label_cost=0.10, gpu_cost=3,
                          budget=100, curve_params=params)
    assert out["labels"] + out["gpu"] <= 100
    assert 0 <= out["accuracy"] <= 1
