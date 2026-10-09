"""Informed Short Demand vs. Loan Supply Friction Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.informed_short_demand.fields import FIELDS
from brain_options.strategies.informed_short_demand.templates import generate_informed_short_demand_candidates


class InformedShortDemandStrategy(BaseStrategy):
    """Exploits the dynamic separation between informed short seller demand and lending supply elasticity."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="informed_short_demand",
            display_name="Informed Short Demand vs. Loan Supply Friction",
            category="securities_lending",
            theory_summary="Disentangles pure informed short conviction from lender supply availability to isolate asymmetric downward pressure.",
            academic_references=[
                "Engelberg, J.E., Reed, A.V., & Ringgenberg, M.C. (2012). How are Shorts Informed? Journal of Financial Economics.",
                "Cohen, L., Diether, K.B., & Malloy, C.J. (2007). Supply and Demand Shifts in the Shorting Market. Journal of Finance.",
                "Rapach, D.E., Ringgenberg, M.C., & Zhou, G. (2016). Short Interest and Aggregate Stock Returns. Journal of Financial Economics.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "MARKET"],
            preferred_decays=[10, 12, 15],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_informed_short_demand_candidates()
