"""
Unit tests for brain_synthesis.regime_engine
"""
from brain_synthesis.regime_engine.detector import MarketRegime, MarketRegimeDetector
from brain_synthesis.regime_engine.dynamic_weights import RegimeAwareWeightTuner


def test_regime_detector():
    detector = MarketRegimeDetector()

    # VIX spike -> HIGH_VOLATILITY
    assert detector.detect_regime(vix_or_iv_mean=28.5) == MarketRegime.HIGH_VOLATILITY

    # Earnings month
    assert detector.detect_regime(vix_or_iv_mean=16.0, is_earnings_month=True) == MarketRegime.EARNINGS_SEASON

    # Strong trend
    assert detector.detect_regime(vix_or_iv_mean=14.0, trend_strength=0.8) == MarketRegime.TRENDING

    # Normal calm market
    assert detector.detect_regime(vix_or_iv_mean=15.0) == MarketRegime.NEUTRAL


def test_regime_aware_weights():
    tuner = RegimeAwareWeightTuner()

    w_vol = tuner.get_weights_for_regime(MarketRegime.HIGH_VOLATILITY)
    assert abs(sum(w_vol) - 1.0) < 1e-6
    # High volatility gives priority to options leg (leg 0)
    assert w_vol[0] > w_vol[1]

    w_earn = tuner.get_weights_for_regime(MarketRegime.EARNINGS_SEASON)
    assert abs(sum(w_earn) - 1.0) < 1e-6
    # Earnings season gives priority to sentiment/revisions leg (leg 1)
    assert w_earn[1] > w_earn[0]
