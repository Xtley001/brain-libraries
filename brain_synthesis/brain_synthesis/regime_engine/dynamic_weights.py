"""
Regime-Aware Adaptive Weight Tuner.
Modulates alpha weights according to the detected market regime (AQuA, Guo et al., 2026).
"""
from __future__ import annotations

from typing import Dict, List, Tuple
from brain_synthesis.regime_engine.detector import MarketRegime


class RegimeAwareWeightTuner:
    """
    Adjusts weights across options, sentiment, and risk model signals
    based on the prevailing market regime.
    """

    DEFAULT_PROFILES: Dict[MarketRegime, Tuple[float, float, float]] = {
        MarketRegime.HIGH_VOLATILITY: (0.55, 0.20, 0.25),  # Heavy options/derivatives skew
        MarketRegime.EARNINGS_SEASON: (0.25, 0.55, 0.20),  # Heavy analyst revisions & PEAD
        MarketRegime.TRENDING: (0.30, 0.30, 0.40),         # Heavy borrow & risk factors
        MarketRegime.NEUTRAL: (0.34, 0.33, 0.33),          # Balanced tri-factor
    }

    def get_weights_for_regime(
        self,
        regime: MarketRegime,
        num_legs: int = 3,
    ) -> List[float]:
        """
        Returns normalized weights summing to 1.0 for the specified regime.
        """
        if num_legs == 3 and regime in self.DEFAULT_PROFILES:
            w1, w2, w3 = self.DEFAULT_PROFILES[regime]
            return [w1, w2, w3]

        # Uniform fallback for arbitrary leg counts
        return [1.0 / num_legs] * num_legs
