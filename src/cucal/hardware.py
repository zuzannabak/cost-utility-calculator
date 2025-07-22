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
