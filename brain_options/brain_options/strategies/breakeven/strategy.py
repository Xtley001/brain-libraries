"""Call Breakeven Hurdle Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.breakeven.fields import FIELDS
from brain_options.strategies.breakeven.templates import generate_breakeven_candidates


class BreakevenStrategy(BaseStrategy):
    """Exploits open-interest weighted call breakeven strike hurdles and dealer barrier adjustments."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="breakeven",
            display_name="Call Breakeven Hurdle Acceleration",
            category="volatility_surface",
            theory_summary="Quantifies open-interest weighted call breakeven distances as dealer barrier hurdles.",
            academic_references=[
                "Tulchinsky, I. et al. (2019). Finding Alphas: A Quantitative Approach to Building Trading Strategies.",
                "Ni, S. X., Pearson, N. D., & Poteshman, A. M. (2005). Stock Price Clustering on Option Expiration Dates. JFE.",
            ],
            preferred_universes=["TOP500", "TOP1000", "TOP3000"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[16, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_breakeven_candidates()
