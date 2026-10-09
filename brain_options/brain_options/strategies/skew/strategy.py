"""Volatility Skew & Smirk Asymmetry Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.skew.fields import FIELDS
from brain_options.strategies.skew.templates import generate_skew_candidates


class SkewStrategy(BaseStrategy):
    """Exploits downside tail risk steepness and call-put volatility smile asymmetries."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="skew",
            display_name="Volatility Skew & Smirk Asymmetry",
            category="volatility_surface",
            theory_summary="Measures cross-sectional tail-risk pricing via OTM put skew steepness and Call-Put IV spreads.",
            academic_references=[
                "Xing, Y., Zhang, X., & Zhao, R. (2010). What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns? JFQA.",
                "Bali, T. G., & Hovakimian, A. (2009). Volatility Spreads and Expected Stock Returns. Management Science.",
                "Bollen, N. P., & Whaley, R. E. (2004). Does Net Buying Pressure Affect the Shape of Implied Volatility Functions? Journal of Finance.",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "INDUSTRY", "MARKET"],
            preferred_decays=[18, 22, 26],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_skew_candidates()
