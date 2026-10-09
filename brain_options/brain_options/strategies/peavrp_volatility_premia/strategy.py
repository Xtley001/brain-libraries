"""Strategy module for Post-Earnings Announcement Volatility Risk Premium Drift."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.peavrp_volatility_premia.fields import FIELDS
from brain_options.strategies.peavrp_volatility_premia.templates import generate_peavrp_volatility_premia_candidates


class PEAVRPVolatilityPremiaStrategy(BaseStrategy):
    """Exploits the post-earnings variance risk premium crush and earnings implied volatility drift."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="peavrp_volatility_premia",
            display_name="Post-Earnings Announcement Volatility Risk Premium Drift",
            category="volatility_surface",
            theory_summary="Isolates the post-earnings volatility crush and variance risk premium resolution across earnings reporting cycles.",
            academic_references=[
                "Ball, Brown (1968): An Empirical Evaluation of Accounting Income Numbers",
                "Bollerslev, Tauchen, Zhou (2009): Expected Stock Returns and Variance Risk Premia",
                "Carr, Wu (2009): Variance Risk Premia",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[12, 15, 20],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_peavrp_volatility_premia_candidates()
