"""Unit tests — brain_sentiment.strategies"""
from brain_sentiment.strategies import (
    SENTIMENT_STRATEGY_REGISTRY,
    generate_modular_candidates,
)


def test_strategy_registry():
    assert len(SENTIMENT_STRATEGY_REGISTRY) >= 6
    for name, strat in SENTIMENT_STRATEGY_REGISTRY.items():
        assert strat.strategy_id == name
        cands = strat.generate_candidates()
        assert len(cands) > 0


def test_generate_modular_candidates():
    cands = generate_modular_candidates()
    assert len(cands) >= 18
