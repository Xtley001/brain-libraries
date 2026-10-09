"""WorldQuant Classic Formulaic Alpha Synthesis Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.formulaic_101.fields import FIELDS
from brain_options.strategies.formulaic_101.templates import generate_formulaic_101_candidates


class Formulaic101Strategy(BaseStrategy):
    """Synthesizes high-frequency and multi-day price-volume interaction operators from WorldQuant canonical alpha literature."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="formulaic_101",
            display_name="WorldQuant Classic Formulaic Alpha Synthesis",
            category="price_volume_dynamics",
            theory_summary="Mathematical cross-sectional price-volume interactions, non-linear geometric rankings, and liquidity exhaustion terms.",
            academic_references=[
                "Kakushadze, Z. (2015). 101 Formulaic Alphas. Wilmott Magazine.",
                "Tulchinsky, I. (2019). Finding Alphas: A Quantitative Approach to Building Trading Strategies. WorldQuant.",
            ],
            preferred_universes=["TOP3000", "USA500", "SP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "MARKET"],
            preferred_decays=[4, 6, 8],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_formulaic_101_candidates()
