"""Unit tests for individual universal axes in isolation."""
from brain_decorrelator.axes.universal import (
    VelocityShiftAxis,
    CalendarSpreadAxis,
    VolumeRegimeAxis,
    VolatilityRegimeAxis,
    NeutralizationRotationAxis,
    CrossSectionalRankAxis,
)


def test_velocity_shift_axis():
    axis = VelocityShiftAxis()
    expr = "ts_decay_linear(rank(close), 10)"
    variants = axis.apply(expr, {})
    assert len(variants) == 3
    assert any("ts_delta(rank(close), 3)" in v for v in variants)
    assert any("ts_delta(rank(close), 5)" in v for v in variants)
    assert any("ts_delta(rank(close), 8)" in v for v in variants)


def test_calendar_spread_axis():
    axis = CalendarSpreadAxis()
    expr = "implied_volatility_call_60 / close"
    variants = axis.apply(expr, {})
    assert len(variants) > 0
    assert any("implied_volatility_call_10" in v or "implied_volatility_call_20" in v for v in variants)


def test_volume_regime_axis():
    axis = VolumeRegimeAxis()
    expr = "rank(close)"
    variants = axis.apply(expr, {})
    assert len(variants) == 3
    assert any("volume > adv20 * 1.0" in v for v in variants)
    assert any("volume > adv20 * 1.15" in v for v in variants)
    assert any("volume > adv20 * 1.25" in v for v in variants)


def test_volatility_regime_axis():
    axis = VolatilityRegimeAxis()
    expr = "rank(close)"
    variants = axis.apply(expr, {})
    assert len(variants) == 2
    assert any("volatility_120 > ts_mean(volatility_120, 20)" in v for v in variants)
    assert any("volatility_120 > ts_mean(volatility_120, 60)" in v for v in variants)


def test_neutralization_rotation_axis():
    axis = NeutralizationRotationAxis()
    expr_sub = "group_neutralize(rank(close), subindustry)"
    variants_sub = axis.apply(expr_sub, {})
    assert len(variants_sub) == 1
    assert "group_neutralize(rank(close), sector)" in variants_sub[0]

    expr_sec = "group_neutralize(rank(close), sector)"
    variants_sec = axis.apply(expr_sec, {})
    assert len(variants_sec) == 1
    assert "group_neutralize(rank(close), subindustry)" in variants_sec[0]


def test_cross_sectional_rank_axis():
    axis = CrossSectionalRankAxis()
    expr = "close / open"
    variants = axis.apply(expr, {})
    assert len(variants) == 2
    assert variants[0] == "group_rank(close / open, subindustry)"
    assert variants[1] == "rank(close / open)"

    # Should skip if already ranked at root
    assert axis.apply("rank(close)", {}) == []
    assert axis.apply("group_rank(close, subindustry)", {}) == []
