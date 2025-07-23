# ── src/curves.py ────────────────────────────────────────────────────────────
"""
Curve utilities for the Cost-Utility Calculator
-----------------------------------------------

* Fit diminishing-returns log curves  y = a · log1p(b·x)
* Load per-resource curves from data/curves.json
* Return paired (label_curve, gpu_curve) for a base task name

Schema assumed in curves.json
-----------------------------
<base>-label : { "label_curve": {a, b}, "rmse": …, "cost_per_unit": … }
<base>-gpu   : { "gpu_curve"  : {a, b}, "rmse": …, "cost_per_unit": … }
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Tuple

import json
import numpy as np
from scipy.optimize import minimize

# ---------------------------------------------------------------------------#
# Log-curve fitting                                                          #
# ---------------------------------------------------------------------------#


def log_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Vectorised log curve  y = a · log(1 + b·x)."""
    return a * np.log1p(b * x)  # log1p is numerically safer for small x


def fit_log_curve(x, y) -> Dict[str, float]:
    """Return {'a':…, 'b':…, 'rmse':…} fitted to (x, y) numpy-like arrays."""
    x, y = np.asarray(x, float), np.asarray(y, float)

    res = minimize(
        lambda p: np.sum((log_model(x, *p) - y) ** 2),
        x0=(1.0, 0.01),
        bounds=((0, None), (0, None)),
    )
    a, b = map(float, res.x)
    rmse = float(np.sqrt(np.mean((log_model(x, a, b) - y) ** 2)))
    return {"a": a, "b": b, "rmse": rmse}


# ---------------------------------------------------------------------------#
# curves.json loader                                                         #
# ---------------------------------------------------------------------------#
def _find_repo_root() -> Path:
    """
    Walk upwards until we locate data/curves.json.
    Allows this module to be imported from any working dir.
    """
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        if (parent / "data" / "curves.json").is_file():
            return parent
    raise FileNotFoundError("Could not locate data/curves.json in parent tree.")


_CURVES_PATH = _find_repo_root() / "data" / "curves.json"


@lru_cache(maxsize=1)
def _curves() -> Dict[str, Dict]:
    return json.loads(_CURVES_PATH.read_text())


# ---------------------------------------------------------------------------#
# Public helper                                                              #
# ---------------------------------------------------------------------------#
def get_curves(base_name: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Parameters
    ----------
    base_name
        ID without ``-label`` / ``-gpu`` suffix, e.g. ``Dragut-2019``.

    Returns
    -------
    (label_curve_dict, gpu_curve_dict)

    Raises
    ------
    KeyError
        If either resource is missing from curves.json.
    """
    curves = _curves()
    lbl_key = f"{base_name}-label"
    gpu_key = f"{base_name}-gpu"

    try:
        return curves[lbl_key]["label_curve"], curves[gpu_key]["gpu_curve"]
    except KeyError as e:
        raise KeyError(
            f"Missing key {e} in curves.json. "
            "Ensure both '-label' and '-gpu' resources exist."
        ) from None
