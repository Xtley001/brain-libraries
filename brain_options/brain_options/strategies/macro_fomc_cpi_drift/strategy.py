"""Strategy module for Macroeconomic & Scheduled Event Drift."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.macro_fomc_cpi_drift.fields import FIELDS
from brain_options.strategies.macro_fomc_cpi_drift.templates import generate_macro_fomc_cpi_drift_candidates


class MacroFOMCCPIDriftStrategy(BaseStrategy):
    """Exploits macroeconomic risk premium resolution, pre-FOMC announcement drift, and CPI volatility cycles."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="macro_fomc_cpi_drift",
            display_name="Macroeconomic & Scheduled Event Drift",
            category="volatility_surface",
            theory_summary="Trades macro risk premium resolution and implied volatility crush around scheduled central bank and macroeconomic announcements.",
            academic_references=[
                "Savor, Wilson (2013): How Much Do News Really Matter? Information and Stock Market Returns",
                "Lucca, Moench (2015): The Pre-FOMC Announcement Drift",
                "Boguth, Carlson, Fisher, Simutin (2019): Macroeconomic Announcements and Volatility Uncertainty",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[10, 14, 18],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_macro_fomc_cpi_drift_candidates()
