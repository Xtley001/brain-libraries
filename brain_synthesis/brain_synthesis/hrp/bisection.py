"""
HRP Recursive Bisection Weight Allocation.
Calculates risk-parity weights without matrix inversion (López de Prado, AFML Chapter 16).
"""
from __future__ import annotations

import math
from typing import List


def get_cluster_variance(cov_matrix: List[List[float]], cluster_indices: List[int]) -> float:
    """Computes equal-weight variance of a cluster subset."""
    k = len(cluster_indices)
    if k == 0:
        return 0.0
    total_var = sum(
        cov_matrix[i][j] for i in cluster_indices for j in cluster_indices
    )
    return max(1e-8, total_var / (k * k))


def recursive_bisection(
    cov_matrix: List[List[float]],
    ordered_indices: List[int],
) -> List[float]:
    """
    Recursively bisects ordered indices to compute HRP weights.
    Returns a list of weights summing to 1.0, matching original matrix order.
    """
    n = len(cov_matrix)
    if n == 0:
        return []
    if n == 1:
        return [1.0]

    weights = {i: 1.0 for i in ordered_indices}
    clusters = [ordered_indices]

    while len(clusters) > 0:
        new_clusters = []
        for cluster in clusters:
            if len(cluster) <= 1:
                continue

            # Bisect cluster into two halves
            mid = len(cluster) // 2
            left = cluster[:mid]
            right = cluster[mid:]

            var_left = get_cluster_variance(cov_matrix, left)
            var_right = get_cluster_variance(cov_matrix, right)

            # Allocate weight inversely proportional to cluster variance
            alpha = 1.0 - var_left / (var_left + var_right)

            for i in left:
                weights[i] *= alpha
            for j in right:
                weights[j] *= (1.0 - alpha)

            if len(left) > 1:
                new_clusters.append(left)
            if len(right) > 1:
                new_clusters.append(right)

        clusters = new_clusters

    # Normalize weights to exactly sum to 1.0
    total_w = sum(weights.values())
    return [weights[i] / total_w for i in range(n)]
