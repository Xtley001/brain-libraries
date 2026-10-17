"""
Market Regime Detector for Dynamic Alpha Synthesis.
Categorizes prevailing market conditions to modulate cross-factor weights.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class MarketRegime(str, Enum):
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    EARNINGS_SEASON = "EARNINGS_SEASON"
    TRENDING = "TRENDING"
    NEUTRAL = "NEUTRAL"


class MarketRegimeDetector:
    """
    Infers the prevailing macro regime from volatility levels, calendar dates,
    and market breadth indicators.
    """

    def detect_regime(
        self,
        vix_or_iv_mean: Optional[float] = None,
        is_earnings_month: bool = False,
        trend_strength: Optional[float] = None,
    ) -> MarketRegime:
        """
        Determines market regime based on input market indicators.
        """
        if vix_or_iv_mean is not None and vix_or_iv_mean > 24.0:
            return MarketRegime.HIGH_VOLATILITY

        if is_earnings_month:
            return MarketRegime.EARNINGS_SEASON

        if trend_strength is not None and abs(trend_strength) > 0.65:
            return MarketRegime.TRENDING

        return MarketRegime.NEUTRAL
