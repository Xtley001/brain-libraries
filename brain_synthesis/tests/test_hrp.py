"""
Unit tests for brain_synthesis.hrp (Hierarchical Risk Parity).
"""
import math
from brain_synthesis.hrp.clustering import (
    compute_correlation_distance_matrix,
    hierarchical_cluster_indices,
)
from brain_synthesis.hrp.bisection import recursive_bisection, get_cluster_variance


def test_correlation_distance_matrix():
    corr = [
        [1.0, 0.8, 0.2],
        [0.8, 1.0, 0.1],
        [0.2, 0.1, 1.0],
    ]
    dist = compute_correlation_distance_matrix(corr)
    # Check diagonals are zero
    for i in range(3):
        assert abs(dist[i][i]) < 1e-9

    # Distance between 0 and 1 (rho=0.8) should be smaller than between 0 and 2 (rho=0.2)
    assert dist[0][1] < dist[0][2]
    # Symmetry
    assert abs(dist[0][1] - dist[1][0]) < 1e-9


def test_hierarchical_cluster_indices():
    # 0 and 1 are highly correlated (0.9), 2 is independent (0.1)
    corr = [
        [1.0, 0.9, 0.1],
        [0.9, 1.0, 0.1],
        [0.1, 0.1, 1.0],
    ]
    indices = hierarchical_cluster_indices(corr)
    assert len(indices) == 3
    # 0 and 1 should be adjacent in the clustering order
    pos0 = indices.index(0)
    pos1 = indices.index(1)
    assert abs(pos0 - pos1) == 1


def test_recursive_bisection_weights():
    # Covariance where asset 0 has high variance (0.09) and asset 1 has low variance (0.01)
    cov = [
        [0.09, 0.0],
        [0.0, 0.01],
    ]
    indices = [0, 1]
    weights = recursive_bisection(cov, indices)
    assert len(weights) == 2
    assert abs(sum(weights) - 1.0) < 1e-6
    # Asset 1 (lower variance) must receive higher HRP weight
    assert weights[1] > weights[0]
