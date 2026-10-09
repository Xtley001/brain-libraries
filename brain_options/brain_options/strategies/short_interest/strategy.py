"""Short Interest & Borrow Squeeze Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.short_interest.fields import FIELDS
from brain_options.strategies.short_interest.templates import generate_short_interest_candidates


class ShortInterestStrategy(BaseStrategy):
    """Exploits equity borrow fee dynamics, short interest z-scores, and short-squeeze breakouts."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="short_interest",
            display_name="Short Interest & Borrow Squeeze Dynamics",
            category="alternative_flow",
            theory_summary="Captures negative sentiment and forced short buy-ins using securities lending borrow fees and days-to-cover.",
            academic_references=[
                "Rapach, D. E., Ringgenberg, M. C., & Zhou, G. (2016). Short Interest and Aggregate Stock Returns. JFE.",
                "Cohen, L., Diether, K. B., & Malloy, C. J. (2007). Supply and Demand Shifts in the Shorting Market. Journal of Finance.",
                "Asquith, P., Pathak, P. A., & Ritter, J. R. (2005). Short Interest, Institutional Ownership, and Stock Returns. JFE.",
            ],
            preferred_universes=["TOP500", "TOP1000", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "INDUSTRY", "MARKET"],
            preferred_decays=[16, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_short_interest_candidates()
