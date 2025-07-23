import pytest
from cucal.optimizer import optimise_allocation


def dummy_capacity(rid: str) -> float:
    return {"rA": 50, "rB": 30, "rC": 100}[rid]


def test_k_resource_exact_fill(monkeypatch):
    # Fake prices so test is deterministic
    monkeypatch.setattr(
        "src.api.k_resource.unit_costs",
        lambda ids: {rid: 1.0 + i for i, rid in enumerate(ids)},  # $1, $2, $3
    )

    plan = optimise_allocation(
        demand=60,
        resource_ids=["rA", "rB", "rC"],
        capacity_for=dummy_capacity,
    )

    assert plan.per_resource == {"rA": 50, "rB": 10}
    assert plan.total_cost == pytest.approx(50 * 1 + 10 * 2)
