"""
Hierarchical Risk Parity (HRP) Tree Clustering.
Implements correlation-distance tree clustering from Marcos López de Prado (AFML).
"""
from __future__ import annotations

import math
from typing import List, Tuple


def compute_correlation_distance_matrix(corr_matrix: List[List[float]]) -> List[List[float]]:
    """
    Computes distance matrix D where d_{i,j} = sqrt(0.5 * (1 - rho_{i,j})).
    D is a proper metric space (distance >= 0, d_{i,i} = 0, triangle inequality holds).
    """
    n = len(corr_matrix)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0.0
            else:
                rho = max(-1.0, min(1.0, corr_matrix[i][j]))
                dist[i][j] = math.sqrt(max(0.0, 0.5 * (1.0 - rho)))
    return dist


def hierarchical_cluster_indices(corr_matrix: List[List[float]]) -> List[int]:
    """
    Performs hierarchical single-linkage agglomerative clustering
    to return a sorted list of item indices (quasi-diagonalization order).
    """
    n = len(corr_matrix)
    if n <= 1:
        return list(range(n))

    dist = compute_correlation_distance_matrix(corr_matrix)

    # Active clusters: each cluster is a list of original item indices
    clusters = [[i] for i in range(n)]

    while len(clusters) > 1:
        # Find pair of clusters with minimum distance
        min_dist = float("inf")
        best_pair = (0, 1)

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                # Single-linkage distance between cluster i and cluster j
                d_ij = min(
                    dist[u][v] for u in clusters[i] for v in clusters[j]
                )
                if d_ij < min_dist:
                    min_dist = d_ij
                    best_pair = (i, j)

        # Merge clusters
        i, j = best_pair
        merged = clusters[i] + clusters[j]
        clusters.pop(j)
        clusters.pop(i)
        clusters.append(merged)

    return clusters[0]
