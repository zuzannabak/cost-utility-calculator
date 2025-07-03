# src/utils.py
"""
Utility functions for cost-utility calculator
"""

from typing import List, Tuple

def parse_curve(cell: str) -> list[tuple[float, float]]:
    """
    '0:0.58;30:0.72'  →  [(0.0, 0.58), (30.0, 0.72)]
    Ignores empty segments and strips whitespace.
    """
    pairs = []
    for pair in str(cell).split(";"):
        if not pair.strip():
            continue
        x_str, y_str = pair.split(":")
        try:
            pairs.append((float(x_str.strip()), float(y_str.strip())))
        except ValueError:
            # Skip malformed points instead of returning strings
            continue
    return pairs


def marginal_gain(x: List[float], y: List[float]) -> List[Tuple[float, float]]:
    """
    Return (x_i, Δy/Δx) after each segment.
    """
    return [(x[i + 1], (y[i + 1] - y[i]) / (x[i + 1] - x[i]))
            for i in range(len(x) - 1)]
