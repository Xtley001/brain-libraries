"""
Unit tests — brain_options.evaluation.filter.passes_quality_gates()

Acceptance criteria
-------------------
AC-1  Returns (True, "") when all 4 gates pass.
AC-2  Returns (False, reason) when sharpe < min_sharpe.
AC-3  Returns (False, reason) when fitness < min_fitness.
AC-4  Returns (False, reason) when turnover < min_turnover.
AC-5  Returns (False, reason) when turnover > max_turnover.
"""
from brain_core.types import SimMetrics
from brain_options.evaluation.filter import passes_quality_gates


def _m(sharpe=1.5, fitness=1.1, turnover=0.30):
    return SimMetrics(status="COMPLETE", sharpe=sharpe, fitness=fitness, turnover=turnover)


def test_ac1_all_pass():
    ok, reason = passes_quality_gates(_m())
    assert ok is True
    assert reason == ""


def test_ac2_sharpe_fail():
    ok, reason = passes_quality_gates(_m(sharpe=1.0))
    assert ok is False
    assert "sharpe" in reason


def test_ac3_fitness_fail():
    ok, reason = passes_quality_gates(_m(fitness=0.9))
    assert ok is False
    assert "fitness" in reason


def test_ac4_turnover_low():
    ok, reason = passes_quality_gates(_m(turnover=0.005))
    assert ok is False
    assert "turnover" in reason


def test_ac5_turnover_high():
    ok, reason = passes_quality_gates(_m(turnover=0.75))
    assert ok is False
    assert "turnover" in reason
