"""Strategy module for R&D Capitalization & Technology Spillovers."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.rd_capitalization_spillovers.fields import FIELDS
from brain_options.strategies.rd_capitalization_spillovers.templates import generate_rd_capitalization_spillovers_candidates


class RDCapitalizationSpilloversStrategy(BaseStrategy):
    """Exploits intangible knowledge capital accumulation, R&D intensity, and industry technological spillovers."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="rd_capitalization_spillovers",
            display_name="R&D Capitalization & Technology Spillovers",
            category="fundamental",
            theory_summary="Measures intangible R&D capital accumulation and technological innovation efficiency to capture long-horizon mispricing.",
            academic_references=[
                "Lev, Sougiannis (1996): The Capitalization, Amortization, and Value-Relevance of R&D",
                "Hirshleifer, Hsu, Li (2013): Innovative Efficiency and Stock Returns",
                "Bloom, Schankerman, Van Reenen (2013): Identifying Technology Spillovers and Product Market Rivalry",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[16, 18, 22],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_rd_capitalization_spillovers_candidates()
