import json
import pathlib
import pytest

CURVES = json.loads((pathlib.Path("data") / "curves.json").read_text())


@pytest.mark.parametrize("task", CURVES.keys())
def test_schema_keys(task):
    entry = CURVES[task]
    has_label = "label_curve" in entry
    has_gpu = "gpu_curve" in entry
    # every resource must expose exactly one curve kind
    assert has_label ^ has_gpu, f"{task} should contain *either* label_curve *or* gpu_curve"
    assert "a" in entry["label_curve"] and "b" in entry["label_curve"]
    assert "a" in entry["gpu_curve"] and "b" in entry["gpu_curve"]
    # rmse optional for GenericNLP, ale musi być float jeżeli jest
    if "rmse" in entry:
        assert isinstance(entry["rmse"], float)
