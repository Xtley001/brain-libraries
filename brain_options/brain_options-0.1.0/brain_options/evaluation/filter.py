"""
Evaluation filter — applies quality gates to SimMetrics.

Gates (all must pass)
---------------------
G1. sharpe    >= filter_min_sharpe      (default 1.25)
G2. fitness   >= filter_min_fitness     (default 1.00)
G3. turnover  >= filter_min_turnover    (default 0.01)
G4. turnover  <= filter_max_turnover    (default 0.70)

Returns True (pass) or False (fail) with a string reason on failure.
"""
from __future__ import annotations
from typing import Tuple
from brain_core.types import SimMetrics


def passes_quality_gates(
    metrics: SimMetrics,
    min_sharpe: float = 1.25,
    min_fitness: float = 1.00,
    min_turnover: float = 0.01,
    max_turnover: float = 0.70,
) -> Tuple[bool, str]:
    """
    Returns (True, "") if all gates pass.
    Returns (False, reason) if any gate fails.
    """
    if metrics.sharpe < min_sharpe:
        return False, f"sharpe {metrics.sharpe:.4f} < {min_sharpe}"
    if metrics.fitness < min_fitness:
        return False, f"fitness {metrics.fitness:.4f} < {min_fitness}"
    if metrics.turnover < min_turnover:
        return False, f"turnover {metrics.turnover:.4f} < {min_turnover}"
    if metrics.turnover > max_turnover:
        return False, f"turnover {metrics.turnover:.4f} > {max_turnover}"
    return True, ""
