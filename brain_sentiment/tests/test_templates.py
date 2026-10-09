"""Unit tests — brain_sentiment.templates and invariant enforcement"""
from brain_sentiment.templates import (
    SentimentCandidate,
    compile_sentiment_invariant,
    generate_template_candidates,
)


def test_compile_sentiment_invariant():
    raw = "snt1_d1_netearningsrevision"
    compiled = compile_sentiment_invariant(raw, default_decay=15)
    assert "group_neutralize(" in compiled
    assert "subindustry" in compiled
    assert "ts_decay_linear(" in compiled


def test_generate_template_candidates():
    candidates = generate_template_candidates()
    assert len(candidates) > 0
    c0 = candidates[0]
    assert isinstance(c0, SentimentCandidate)
    assert c0.universe in ("TOP3000", "TOP2000")
    assert c0.neutralization in ("SUBINDUSTRY", "SECTOR")
    assert "trade_when" in c0.expression or "group_neutralize" in c0.expression
