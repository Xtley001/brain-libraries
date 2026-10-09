"""Put-Call Ratio & Order Flow Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.pcr_flow.fields import FIELDS
from brain_options.strategies.pcr_flow.templates import generate_pcr_flow_candidates


class PCRFlowStrategy(BaseStrategy):
    """Exploits options order flow velocity, put-call imbalances, and smart money positioning."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="pcr_flow",
            display_name="Put-Call Ratio & Order Flow Imbalances",
            category="order_flow",
            theory_summary="Extracts directional smart-money signals from volume-to-open-interest surges and capitulation spikes.",
            academic_references=[
                "Pan, J., & Poteshman, A. M. (2006). The Information in Option Volume for Future Stock Prices. Journal of Finance.",
                "Garleanu, N., & Pedersen, L. H. (2009). Margin-Based Asset Pricing and Deviations from the Law of One Price. RFS.",
                "Johnson, M. A., & So, E. C. (2012). The Option to Stock Volume Ratio and Future Returns. Journal of Financial Economics.",
            ],
            preferred_universes=["TOP2000", "TOP3000", "TOP1000"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[18, 22, 25],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_pcr_flow_candidates()
