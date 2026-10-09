"""Strategy module for Capital Investment & Asset Growth Anomalies."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.capex_asset_growth.fields import FIELDS
from brain_options.strategies.capex_asset_growth.templates import generate_capex_asset_growth_candidates


class CapexAssetGrowthStrategy(BaseStrategy):
    """Exploits the asset growth anomaly and abnormal capital investment drag on equity returns."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="capex_asset_growth",
            display_name="Capital Investment & Asset Growth Anomalies",
            category="fundamental",
            theory_summary="Shorts over-investing empire-building firms with massive balance sheet asset expansion and longs disciplined capital allocators.",
            academic_references=[
                "Titman, Wei, Xie (2004): Capital Investments and Stock Returns",
                "Cooper, Gulen, Schill (2008): Asset Growth and the Cross-Section of Stock Returns",
                "Polk, Sapienza (2009): The Stock Market and Corporate Investment: A Test of Catering Theory",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[16, 20, 24],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_capex_asset_growth_candidates()
