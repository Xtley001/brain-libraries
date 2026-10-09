"""Network Graph Clustering & Co-Movement Lead-Lag Momentum Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.network_momentum.fields import FIELDS
from brain_options.strategies.network_momentum.templates import generate_network_momentum_candidates


class NetworkMomentumStrategy(BaseStrategy):
    """Exploits cluster co-movement dynamics and lead-lag return dispersion across equity graph communities."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="network_momentum",
            display_name="Network Graph Clustering & Co-Movement Lead-Lag Momentum",
            category="graph_clustering",
            theory_summary="Quantifies peer network cluster centroids and relative lead-lag dispersion to trade momentum propagation and mean reversion.",
            academic_references=[
                "Lopez de Prado, M. (2018). Advances in Financial Machine Learning. John Wiley & Sons.",
                "Lead-Lag Detection Network Clustering Research Papers (Institutional Quantitative Finance).",
                "Tulchinsky, I. (2019). Finding Alphas: A Quantitative Approach to Building Trading Strategies. WorldQuant.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET", "NONE"],
            preferred_decays=[5, 10, 15],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_network_momentum_candidates()
