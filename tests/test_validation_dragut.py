import subprocess
import sys
import json
import pathlib
import cucal.optimizer as opt


def test_validation_dragut_passes(tmp_path):
    """
    Calls the CLI entry-point and expects a 0 return-code.
    Captures stdout so we can debug if it fails.
    """
    result = subprocess.run(
        [sys.executable, "-m", "cucal.validate", "dragut", "--budget", "1500", "--time", "24"],
        capture_output=True,
        text=True,
    )
    print("\n---- validation output ----\n", result.stdout)   # shows up only if test fails
    assert result.returncode == 0, result.stderr

DATA = pathlib.Path("data/curves.json")

def test_rmse_under_0_05():
    curves = json.loads(DATA.read_text())["Dragut-2019-label"]
    assert curves["rmse"] < 0.05, "Curve fit is too loose"

def test_sim_accuracy_close():
    res = opt.optimise_budget(
        label_cost=0.02,
        gpu_cost=1.40,
        budget=400,
        curve_label={"a": 0.7067, "b": 0.0140},
        curve_gpu={"a": 0.6755, "b": 0.5527},
        gamma=5,
    )
    assert abs(res["accuracy"] - 0.84) < 0.04