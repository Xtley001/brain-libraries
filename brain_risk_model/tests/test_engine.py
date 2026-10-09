"""Unit tests — brain_risk_model.engine.RiskModelAlphaEngine"""
from brain_risk_model.engine import RiskModelAlphaEngine


def test_engine_candidate_generation():
    engine = RiskModelAlphaEngine()
    cands = engine.generate_candidates(count=5)
    assert len(cands) == 5
    for c in cands:
        assert c.expression
        assert c.family


def test_engine_candidate_decorrelation():
    engine = RiskModelAlphaEngine()
    cand = engine.generate_candidates(count=1)[0]
    variants = engine.decorrelate_candidate(cand, base_sharpe=1.45)
    assert isinstance(variants, list)
    assert len(variants) > 0
