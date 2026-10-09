"""Multi-Tenor & Cross-Asset Hybrid Confluence Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.hybrid_confluence.fields import FIELDS
from brain_options.strategies.hybrid_confluence.templates import generate_hybrid_confluence_candidates


class HybridConfluenceStrategy(BaseStrategy):
    """Synthesizes cross-asset confluence across options surfaces, borrow fees, and fundamental revisions."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="hybrid_confluence",
            display_name="Cross-Asset Hybrid Confluence",
            category="cross_asset",
            theory_summary="Fuses multi-tenor options dynamics with cash borrow fee constraints and analyst revisions.",
            academic_references=[
                "Muravyev, D. (2016). Order Flow and Price Discovery in Options and Equity Markets. RFS.",
                "Easley, D., O'Hara, M., & Srinivas, P. S. (1998). Option Volume and Stock Prices. Journal of Finance.",
            ],
            preferred_universes=["TOPSP500", "TOP1000", "TOP2000"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[18, 22, 26],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_hybrid_confluence_candidates()
