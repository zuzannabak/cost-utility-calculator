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
        [sys.executable, "-m", "cucal.validate", "dragut", "--budget", "1500",
         "--time", "24", "--gamma", "15"],
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
    curves = json.loads(DATA.read_text())
    lbl = curves["Dragut-2019-label"]
    gpu = curves["Dragut-2019-gpu"]

    res = opt.optimise_budget(
        label_cost=lbl["cost_per_unit"],
        gpu_cost=gpu["cost_per_unit"],
        budget=400,
        curve_label=lbl["label_curve"],
        curve_gpu=gpu["gpu_curve"],
        gamma=5,
    )
    # allow ±7 % in case curves get re-fitted later
    exp = res["accuracy"]
    assert 0.88 <= exp <= 0.98
