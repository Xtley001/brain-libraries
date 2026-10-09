"""Strategy module for Volume-Synchronized Probability of Toxicity (VPIN) Order Flow."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.order_flow_vpin.fields import FIELDS
from brain_options.strategies.order_flow_vpin.templates import generate_order_flow_vpin_candidates


class OrderFlowVPINStrategy(BaseStrategy):
    """Exploits volume-synchronized probability of toxicity, informed trade arrival, and market maker adverse selection."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="order_flow_vpin",
            display_name="Volume-Synchronized Probability of Toxicity (VPIN) Order Flow",
            category="microstructure",
            theory_summary="Quantifies informed order flow clustering and toxic order arrivals across trade-volume buckets.",
            academic_references=[
                "Easley, Lopez de Prado, O'Hara (2012): Flow Toxicity and Liquidity in a High-Frequency World",
                "Easley, Lopez de Prado, O'Hara (2011): The Microstructure of the Flash Crash",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[10, 15, 20],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_order_flow_vpin_candidates()
