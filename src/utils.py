# src/utils.py
"""
Utility functions for cost-utility calculator
"""

from typing import List, Tuple

def parse_curve(cell: str) -> List[Tuple[float, float]]:
    """
    Convert a semicolon-separated string of 'x:y' pairs to a list of tuples.

    Example
    -------
    '0:0.58;30:0.72' -> [(0, 0.58), (30, 0.72)]
    """
    pts = []
    for pair in str(cell).split(";"):
        if pair:
            x_str, y_str = pair.split(":")
            pts.append((float(x_str), float(y_str)))
    return pts


def marginal_gain(x: List[float], y: List[float]) -> List[Tuple[float, float]]:
    """
    Return (x_i, Δy/Δx) after each segment.
    """
    return [(x[i + 1], (y[i + 1] - y[i]) / (x[i + 1] - x[i]))
            for i in range(len(x) - 1)]
