import subprocess, sys, textwrap, pathlib

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
