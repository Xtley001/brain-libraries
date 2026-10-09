"""
Dynamic Multi-Leg Alpha Synthesizer.
Fuses arbitrary single-domain signals into cross-asset orthogonal super-alphas.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from brain_core.types import AlphaCandidate
from brain_synthesis.apex_generator import ApexCandidate

log = logging.getLogger("brain_synthesis.combiner")


class DynamicSynthesizer:
    """
    Enables arbitrary weighted combination of alpha signals across domains.
    Automatically standardizes sub-signals via rank() and wraps in group neutralization.
    """

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
