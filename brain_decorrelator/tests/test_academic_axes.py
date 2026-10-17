"""
Unit tests for the new academic orthogonalization axes in brain_decorrelator v0.2.0.
"""
from brain_decorrelator.axes.sector_demean import SectorDemeanAxis
from brain_decorrelator.axes.regime_conditional import VolatilityRegimeScalingAxis
from brain_decorrelator.axes.gram_schmidt import GramSchmidtAxis
from brain_decorrelator.axes.decay_extension import DecayDilationAxis


def test_sector_demean_axis():
    axis = SectorDemeanAxis()
    res = axis.apply("group_neutralize(rank(close), subindustry)", {})
    assert len(res) == 1
    assert "group_rank(rank(close), sector)" in res[0]
    assert "subindustry" in res[0]


def test_volatility_regime_scaling_axis():
    axis = VolatilityRegimeScalingAxis()
    res = axis.apply("rank(close)", {})
    assert len(res) == 1
    assert "ts_std_dev(returns, 60)" in res[0]


def test_gram_schmidt_axis():
    axis = GramSchmidtAxis()
    res = axis.apply("group_neutralize(rank(close), subindustry)", {})
    assert len(res) == 1
    assert "beta_last_60_days_spy" in res[0]


def test_decay_dilation_axis():
    axis = DecayDilationAxis()
    res = axis.apply("ts_decay_linear(close, 5)", {})
    assert len(res) == 4
    decays = [18, 22, 26, 30]
    for d in decays:
        assert any(f"ts_decay_linear(close, {d})" in r for r in res)
