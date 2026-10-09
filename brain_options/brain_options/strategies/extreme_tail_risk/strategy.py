"""Extreme Tail Risk Asymmetry & OTM Put Jump Diffusion Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.extreme_tail_risk.fields import FIELDS
from brain_options.strategies.extreme_tail_risk.templates import generate_extreme_tail_risk_candidates


class ExtremeTailRiskStrategy(BaseStrategy):
    """Exploits structural skew smirk pricing and asymmetric downside jump-diffusion intensity."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="extreme_tail_risk",
            display_name="Extreme Tail Risk Asymmetry & OTM Put Jump Diffusion",
            category="volatility_surface",
            theory_summary="Quantifies disaster insurance premiums via OTM put vs ATM call implied volatility smirks to forecast crash risk.",
            academic_references=[
                "Bakshi, G., Kapadia, N., & Madan, D. (2003). Stock Return Characteristics, Skew Laws, and the Differential Pricing of Individual Equity Options. Review of Financial Studies.",
                "Xing, Y., Zhang, X., & Zhao, R. (2010). What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns? Journal of Financial and Quantitative Analysis.",
                "Bennett, C. (2014). Trading Volatility: Correlation, Term Structure and Skew.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[8, 10, 12],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_extreme_tail_risk_candidates()
