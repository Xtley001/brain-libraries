"""Strategy module for Structural Credit Risk & Distance to Default."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.distance_to_default_debt.fields import FIELDS
from brain_options.strategies.distance_to_default_debt.templates import generate_distance_to_default_debt_candidates


class DistanceToDefaultDebtStrategy(BaseStrategy):
    """Exploits Merton structural credit default likelihood, leverage distress, and debt coverage."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="distance_to_default_debt",
            display_name="Structural Credit Risk & Distance to Default",
            category="fundamental",
            theory_summary="Computes structural distance-to-default proxies using balance sheet obligations and options implied volatility surfaces.",
            academic_references=[
                "Merton (1974): On the Pricing of Corporate Debt: The Risk Structure of Interest Rates",
                "Bharath, Shumway (2008): Forecasting Default with the Merton KMV Models",
                "Nieto, Rodriguez (2013): Options-Implied Default Probabilities",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[14, 18, 22],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_distance_to_default_debt_candidates()
