"""
Global run-time knobs that other modules can import.

Feel free to expose more constants here as the project grows.
"""

# Parallel-efficiency of the GPU cluster (0 < EFF ≤ 1).
DEFAULT_CLUSTER_EFF: float = 0.90

__all__ = ["DEFAULT_CLUSTER_EFF"]
