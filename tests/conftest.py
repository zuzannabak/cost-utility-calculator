import pytest


@pytest.fixture(autouse=True)
def patch_unit_costs(monkeypatch):
    monkeypatch.setattr(
        "src.api.k_resource.unit_costs",
        lambda ids: {rid: 42.0 for rid in ids},  # constant price
    )
