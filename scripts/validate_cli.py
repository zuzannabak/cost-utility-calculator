"""
Regression guard: run the public CLI once per case-study and assert that
the JSON output is well-formed *and* respects any wall-clock limit.

pytest will discover this file automatically (see step 3-B).
"""

from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

import pytest

# --- discover available tasks ---------------------------------------------
META = json.loads((Path("data") / "curves.json").read_text())
TASKS = sorted({k.rsplit("-", 1)[0] for k in META})

# --- helpers ---------------------------------------------------------------
REQUIRED_KEYS = {
    "accuracy",
    "accuracy_ci",
    "labels",
    "label_dollars",
    "gpu_hours",
    "gpu_dollars",
    "wall_clock_hours",
}

def run_cli(task: str, budget: int = 100, wall: int = 0, eff: int = 100) -> dict:
    """
    Call: python -m cucal --budget {budget} --time {wall} --eff {eff} {task}
    The CLI prints *only* the JSON plan to stdout.
    """
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "cucal",
            "--budget",
            str(budget),
            "--time",
            str(wall),
            "--eff",
            str(eff),
            task,
        ],
        text=True,
    )
    return json.loads(out)

# --- tests -----------------------------------------------------------------
@pytest.mark.parametrize("task", TASKS)
def test_cli_contract(task):
    """Ensure CLI returns valid structure and obeys wall-clock cap."""
    res = run_cli(task)

    # structure
    missing = REQUIRED_KEYS - res.keys()
    assert not missing, f"{task}: missing {missing}"

    # if user passed --time 0 the field may be None
    if (wall := res["wall_clock_hours"]) is not None:
        assert wall >= 0, f"{task}: negative wall-clock?"
        # 0 in CLI means "no limit"; guard only when > 0
        if wall > 0:
            assert wall <= 168, f"{task}: exceeded weekly cap"

