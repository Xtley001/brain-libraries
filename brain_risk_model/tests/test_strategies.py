"""Unit tests — brain_risk_model.strategies"""
from brain_risk_model.strategies import (
    RISK_MODEL_STRATEGY_REGISTRY,
    generate_modular_candidates,
)


def test_strategy_registry():
    assert len(RISK_MODEL_STRATEGY_REGISTRY) >= 6
    for name, strat in RISK_MODEL_STRATEGY_REGISTRY.items():
        assert strat.strategy_id == name
        cands = strat.generate_candidates()
        assert len(cands) > 0


def test_generate_modular_candidates():
    cands = generate_modular_candidates()
    assert len(cands) >= 18
