"""
Unit tests — brain_options.pipeline.engine.OptionsAlphaEngine
"""
from brain_options.pipeline.engine import OptionsAlphaEngine
from brain_core.types import SimMetrics


def test_engine_candidate_generation():
    engine = OptionsAlphaEngine()
    cands = engine.generate_candidates(count=5)
    assert len(cands) == 5
    for c in cands:
        assert c.expression
        assert c.universe


def test_engine_decorrelate():
    engine = OptionsAlphaEngine()
    cands = engine.generate_candidates(count=1)
    variants = engine.decorrelate_candidate(cands[0], base_sharpe=1.45)
    assert isinstance(variants, list)
    assert len(variants) > 0


def test_engine_quality_gates():
    engine = OptionsAlphaEngine()
    m_pass = SimMetrics(status="COMPLETE", sharpe=1.4, fitness=1.2, turnover=0.25)
    ok, reason = engine.evaluate_gates(m_pass)
    assert ok is True

    m_fail = SimMetrics(status="COMPLETE", sharpe=0.8, fitness=1.2, turnover=0.25)
    ok, reason = engine.evaluate_gates(m_fail)
    assert ok is False
