"""Unit tests — brain_sentiment.engine.SentimentAlphaEngine"""
from brain_sentiment.engine import SentimentAlphaEngine


def test_engine_candidate_generation():
    engine = SentimentAlphaEngine()
    cands = engine.generate_candidates(count=5)
    assert len(cands) == 5
    for c in cands:
        assert c.expression
        assert c.family


def test_engine_candidate_decorrelation():
    engine = SentimentAlphaEngine()
    cand = engine.generate_candidates(count=1)[0]
    variants = engine.decorrelate_candidate(cand, base_sharpe=1.45)
    assert isinstance(variants, list)
    assert len(variants) > 0
