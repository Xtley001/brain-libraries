"""
HRP (Hierarchical Risk Parity) module for brain_synthesis v0.2.0.
"""
from brain_synthesis.hrp.clustering import (
    compute_correlation_distance_matrix,
    hierarchical_cluster_indices,
)
from brain_synthesis.hrp.bisection import recursive_bisection

__all__ = [
    "compute_correlation_distance_matrix",
    "hierarchical_cluster_indices",
    "recursive_bisection",
]
