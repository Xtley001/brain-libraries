"""Corporate Insider Cluster Buying Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.insider_cluster_buying.fields import FIELDS
from brain_options.strategies.insider_cluster_buying.templates import generate_insider_cluster_buying_candidates


class InsiderClusterBuyingStrategy(BaseStrategy):
    """Exploits open-market corporate insider cluster buying and opportunistic transaction dynamics."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="insider_cluster_buying",
            display_name="Corporate Insider Cluster Buying & Opportunistic Trading",
            category="insider_sentiment",
            theory_summary="Captures open-market purchases by corporate executives (CEO/CFO), filtering out routine automated plans to isolate opportunistic smart-money flow.",
            academic_references=[
                "Cohen, L., Malloy, C., & Pomorski, L. (2012). Decoding Inside Information. Journal of Finance.",
                "Lakonishok, J., & Lee, I. (2001). Are Insider Trades Informative? Review of Financial Studies.",
                "Seyhun, H.N. (1998). Investment Intelligence from Insider Trading. MIT Press.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[15, 20, 25],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_insider_cluster_buying_candidates()
