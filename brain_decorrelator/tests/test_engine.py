"""
Unit tests — brain_decorrelator engine.

Acceptance criteria
-------------------
AC-1  Engine with no registered axes returns [].
AC-2  VelocityShiftAxis produces variants when ts_decay_linear is present.
AC-3  Engine deduplicates identical variants across axes.
AC-4  CalendarSpreadAxis produces variants when a tenor field is present.
AC-5  VolumeRegimeAxis is skipped when "volume > adv20" already in expr.
AC-6  NeutralizationRotationAxis swaps subindustry → sector.
"""
import pytest

# Import universal axes so they register themselves
import brain_decorrelator.axes.universal  # noqa: F401

from brain_decorrelator import DecorrelationEngine


ENGINE = DecorrelationEngine()


def test_ac2_velocity_shift():
    expr = "ts_decay_linear(implied_volatility_mean_30, 10)"
    results = ENGINE.generate_orthogonal_variants(expr, "iv_level", base_sharpe=1.6)
    axis_names = [r.axis_name for r in results]
    assert "Axis 1 (Velocity Shift)" in axis_names
    # Should produce 3 lookback variants (3, 5, 8)
    velocity_results = [r for r in results if r.axis_name == "Axis 1 (Velocity Shift)"]
    assert len(velocity_results) == 3


def test_ac3_deduplication():
    expr = "ts_decay_linear(close, 10)"
    results = ENGINE.generate_orthogonal_variants(expr, "momentum", base_sharpe=1.5)
    exprs = [r.expression for r in results]
    assert len(exprs) == len(set(exprs)), "Duplicate variants found"


def test_ac4_calendar_spread():
    expr = "rank(implied_volatility_mean_30)"
    results = ENGINE.generate_orthogonal_variants(expr, "iv_level", base_sharpe=1.4)
    axis_names = [r.axis_name for r in results]
    assert "Axis 2 (Calendar Curve Spread)" in axis_names


def test_ac5_volume_gate_skipped_when_already_present():
    expr = "trade_when(volume > adv20 * 1.0, rank(close), -1)"
    results = ENGINE.generate_orthogonal_variants(expr, "momentum", base_sharpe=1.5)
    axis_names = [r.axis_name for r in results]
    assert "Axis 3 (Volume Regime Gate)" not in axis_names


def test_ac6_neutralization_rotation():
    expr = "group_neutralize(rank(close), subindustry)"
    results = ENGINE.generate_orthogonal_variants(expr, "momentum", base_sharpe=1.5)
    axis_names = [r.axis_name for r in results]
    assert "Axis 5 (Neutralization Rotation)" in axis_names
    rot = [r for r in results if r.axis_name == "Axis 5 (Neutralization Rotation)"]
    assert "sector" in rot[0].expression


def test_result_fields_populated():
    expr = "ts_decay_linear(close, 10)"
    results = ENGINE.generate_orthogonal_variants(
        expr, "momentum", base_sharpe=1.7, colliding_id="alpha_abc123"
    )
    assert len(results) > 0
    r = results[0]
    assert "Decorrelated(momentum)" in r.archetype_name
    assert "1.70" in r.hypothesis
    assert r.base_alpha_id == "alpha_abc123"
