"""Term Structure & Variance Risk Premium Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.term_structure.fields import FIELDS
from brain_options.strategies.term_structure.templates import generate_term_structure_candidates


class TermStructureStrategy(BaseStrategy):
    """Exploits structural mispricings across option tenors and the variance risk premium."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="term_structure",
            display_name="Volatility Term Structure & Variance Risk Premium",
            category="volatility_surface",
            theory_summary="Captures IV term slope inversions and structural variance risk premia across equity options surfaces.",
            academic_references=[
                "Carr, P., & Wu, L. (2009). Variance Risk Premiums. Review of Financial Studies.",
                "Sinclair, E. (2013). Volatility Trading. John Wiley & Sons.",
                "Bennett, C. (2014). Trading Volatility: Correlation, Term Structure and Skew.",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[16, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_term_structure_candidates()
