import json
import pathlib
import pytest

CURVES = json.loads((pathlib.Path("data") / "curves.json").read_text())


@pytest.mark.parametrize("task", CURVES.keys())
def test_schema_keys(task):
    entry = CURVES[task]
    assert "label_curve" in entry and "gpu_curve" in entry
    assert "a" in entry["label_curve"] and "b" in entry["label_curve"]
    assert "a" in entry["gpu_curve"] and "b" in entry["gpu_curve"]
    # rmse optional for GenericNLP, ale musi być float jeżeli jest
    if "rmse" in entry:
        assert isinstance(entry["rmse"], float)
