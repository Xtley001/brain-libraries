"""Analyst Consensus Revisions & PEAD Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.analyst_revisions.fields import FIELDS
from brain_options.strategies.analyst_revisions.templates import generate_analyst_revisions_candidates


class AnalystRevisionsStrategy(BaseStrategy):
    """Exploits sell-side analyst estimate revisions, disagreement dispersion, and price target upside."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="analyst_revisions",
            display_name="Analyst Consensus Revisions & PEAD",
            category="fundamental_momentum",
            theory_summary="Captures post-earnings announcement drift and sluggish analyst expectation revisions.",
            academic_references=[
                "Givoly, D., & Lakonishok, J. (1979). The Information Content of Financial Analysts' Forecasts. JAE.",
                "Diether, K. B., Malloy, C. J., & Scherbina, A. (2002). Differences of Opinion and the Cross Section of Stock Returns. JF.",
            ],
            preferred_universes=["TOPSP500", "TOP500", "TOP1000"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "INDUSTRY", "MARKET"],
            preferred_decays=[18, 24, 30],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_analyst_revisions_candidates()
