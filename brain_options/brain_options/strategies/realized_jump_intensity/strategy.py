"""Strategy module for Realized High-Frequency Jump Intensity & Skew."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.realized_jump_intensity.fields import FIELDS
from brain_options.strategies.realized_jump_intensity.templates import generate_realized_jump_intensity_candidates


class RealizedJumpIntensityStrategy(BaseStrategy):
    """Exploits realized price jump discontinuities, volatility asymmetry, and realized skewness."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="realized_jump_intensity",
            display_name="Realized High-Frequency Jump Intensity & Skew",
            category="volatility_surface",
            theory_summary="Decomposes price variation into continuous and jump components to exploit liquidity replenishment following jump dislocations.",
            academic_references=[
                "Amaya, Christoffersen, Jacobs, Vasquez (2015): Does Realized Skewness Predict the Cross-Section of Equity Returns?",
                "Nonejad (2013): Good and Bad Volatility and the Cross-Section of Stock Returns",
                "Bollerslev, Li, Zhao (2020): Good Volatility, Bad Volatility, and the Cross-Section of Returns",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[10, 12, 16],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_realized_jump_intensity_candidates()
