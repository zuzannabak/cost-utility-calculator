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
    assert has_label ^ has_gpu, (
        f"{task} should contain *either* label_curve *or* gpu_curve"
    )

    curve_key = "label_curve" if has_label else "gpu_curve"
    assert "a" in entry[curve_key] and "b" in entry[curve_key]

    # rmse is optional but must be a float when presentif "rmse" in entry:
    if "rmse" in entry:
        assert isinstance(entry["rmse"], float)
