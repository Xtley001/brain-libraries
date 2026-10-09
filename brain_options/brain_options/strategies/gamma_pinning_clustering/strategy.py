"""Strategy module for Gamma Imbalance & Expiration Strike Pinning."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.gamma_pinning_clustering.fields import FIELDS
from brain_options.strategies.gamma_pinning_clustering.templates import generate_gamma_pinning_clustering_candidates


class GammaPinningClusteringStrategy(BaseStrategy):
    """Exploits option market maker gamma hedging constraints, max-pain strike magnetism, and expiration pinning."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="gamma_pinning_clustering",
            display_name="Gamma Imbalance & Expiration Strike Pinning",
            category="volatility_surface",
            theory_summary="Measures aggregate dealer gamma imbalances and expiration strike gravitational pull.",
            academic_references=[
                "Ni, Pearson, Poteshman (2005): Stock Price Clustering on Option Expiration Dates",
                "Avellaneda, Lipkin (2003): A Market-Induced Mechanism for Stock Pinning",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[10, 15, 20],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_gamma_pinning_clustering_candidates()
