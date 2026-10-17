"""
Dynamic Multi-Leg Alpha Synthesizer (v0.2.0).
Fuses arbitrary single-domain signals into cross-asset orthogonal super-alphas.
Supports explicit weighting, HRP (Hierarchical Risk Parity), and regime-adaptive synthesis.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from brain_core.types import AlphaCandidate
from brain_synthesis.apex_generator import ApexCandidate
from brain_synthesis.hrp.clustering import hierarchical_cluster_indices
from brain_synthesis.hrp.bisection import recursive_bisection
from brain_synthesis.regime_engine.detector import MarketRegime
from brain_synthesis.regime_engine.dynamic_weights import RegimeAwareWeightTuner

log = logging.getLogger("brain_synthesis.combiner")


class DynamicSynthesizer:
    """
    Enables arbitrary weighted combination of alpha signals across domains.
    Supports manual weighting, Hierarchical Risk Parity (HRP), and regime-aware weighting.
    """

    def __init__(self):
        self.regime_tuner = RegimeAwareWeightTuner()

    def synthesize(
        self,
        legs: List[Tuple[AlphaCandidate, float]],
        name: str = "Synthesized_Multi_Leg",
        universe: str = "TOP3000",
        neutralization: str = "SUBINDUSTRY",
        decay: int = 12,
    ) -> ApexCandidate:
        """
        Combine multiple (AlphaCandidate, weight) pairs into a composite apex candidate.
        Example:
            legs = [(option_cand, 0.5), (sentiment_cand, 0.3), (risk_cand, -0.2)]
        """
        if not legs:
            raise ValueError("At least one leg is required for synthesis")

        expr_terms = []
        for cand, weight in legs:
            sign = "+" if weight >= 0 else "-"
            abs_w = abs(weight)
            # Wrap inner expression in rank if not already ranked
            inner = cand.expression.strip()
            if not inner.startswith("rank("):
                inner = f"rank({inner})"
            expr_terms.append(f"{sign} {abs_w:.2f} * {inner}")

        composite_inner = " ".join(expr_terms).lstrip("+ ").strip()
        group = neutralization.lower()
        full_expr = f"group_neutralize(rank({composite_inner}), {group})"

        return ApexCandidate(
            expression=full_expr,
            archetype_name=name,
            name=name,
            hypothesis=f"Multi-leg synthesis fusing {len(legs)} cross-asset signals.",
            universe=universe,
            neutralization=neutralization.upper(),
            decay=decay,
            category="hybrid_tri_factor",
            value_score=8.5,
        )

    def synthesize_hrp(
        self,
        candidates: List[AlphaCandidate],
        cov_matrix: List[List[float]],
        name: str = "HRP_Synthesized_Apex",
        universe: str = "TOP3000",
        neutralization: str = "SUBINDUSTRY",
        decay: int = 15,
    ) -> ApexCandidate:
        """
        Synthesizes a composite alpha using Hierarchical Risk Parity (HRP) weights.
        Automatically performs tree clustering and recursive bisection without matrix inversion.
        """
        if len(candidates) != len(cov_matrix):
            raise ValueError(f"Candidates count ({len(candidates)}) must match cov_matrix dimension ({len(cov_matrix)})")

        ordered_indices = hierarchical_cluster_indices(cov_matrix)
        hrp_weights = recursive_bisection(cov_matrix, ordered_indices)

        legs = list(zip(candidates, hrp_weights))
        return self.synthesize(
            legs=legs,
            name=name,
            universe=universe,
            neutralization=neutralization,
            decay=decay,
        )

    def synthesize_regime(
        self,
        candidates: List[AlphaCandidate],
        regime: MarketRegime,
        name: str = "Regime_Adaptive_Apex",
        universe: str = "TOP3000",
        neutralization: str = "SUBINDUSTRY",
        decay: int = 15,
    ) -> ApexCandidate:
        """
        Synthesizes a composite alpha with weights adapted to the specified market regime.
        """
        weights = self.regime_tuner.get_weights_for_regime(regime, num_legs=len(candidates))
        legs = list(zip(candidates, weights))
        return self.synthesize(
            legs=legs,
            name=f"{name}_{regime.value}",
            universe=universe,
            neutralization=neutralization,
            decay=decay,
        )
