"""
Narzędzia: wczytywanie hardware.json + proste obliczenia energii.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

# <repo_root>/src/resources/hardware.json
_HARDWARE_PATH = Path(__file__).resolve().parent.parent / "resources" / "hardware.json"


def load_hardware() -> Dict[str, Dict[str, Any]]:
    """Zwraca słownik {nazwa_gpu: {"power": int}}."""
    with _HARDWARE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def calculate_energy(power_w: float, gpu_hours: float) -> float:
    """
    Energia (Wh) = pobór mocy [W] × czas działania [h].
    """
    return power_w * gpu_hours


# ---------------------------------------------------------------------
# 🆕 Carbon calculator
# ---------------------------------------------------------------------
def co2_equivalent(energy_wh: float, gco2_per_kwh: float) -> float:
    """Return g CO₂ for the given **energy_wh** (Wh).

    Parameters
    ----------
    energy_wh : float
        Watt-hours consumed.
    gco2_per_kwh : float
        Grid-intensity (grams CO₂ per kWh), user-supplied.

    Examples
    --------
    >>> co2_equivalent(12_000, gco2_per_kwh=450)
    5400.0
    """
    return energy_wh / 1_000 * gco2_per_kwh
