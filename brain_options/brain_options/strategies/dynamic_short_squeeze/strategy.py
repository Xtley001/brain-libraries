"""Strategy module for Dynamic Short Squeeze & Borrow Fee Convexity."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.dynamic_short_squeeze.fields import FIELDS
from brain_options.strategies.dynamic_short_squeeze.templates import generate_dynamic_short_squeeze_candidates


class DynamicShortSqueezeStrategy(BaseStrategy):
    """Exploits mandatory short recall mechanics, borrow fee acceleration, and asymmetric squeeze dynamics."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="dynamic_short_squeeze",
            display_name="Dynamic Short Squeeze & Borrow Fee Convexity",
            category="microstructure",
            theory_summary="Isolates convex borrow fee spikes and short float crowding to capture non-discretionary short squeeze runs.",
            academic_references=[
                "Engelberg, Reed, Ringgenberg (2018): Short-Selling Risk",
                "Kolasinski, Reed, Ringgenberg (2013): Supply and Search in the Equity Lending Market",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[12, 16, 20],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_dynamic_short_squeeze_candidates()
