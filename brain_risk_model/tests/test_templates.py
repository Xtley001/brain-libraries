"""Unit tests — brain_risk_model.templates and invariant enforcement"""
from brain_risk_model.templates import (
    RiskModelCandidate,
    compile_risk_model_invariant,
    generate_template_candidates,
)


def test_compile_risk_model_invariant():
    raw = "beta_last_60_days_spy"
    compiled = compile_risk_model_invariant(raw, default_decay=15)
    assert "group_neutralize(" in compiled
    assert "subindustry" in compiled
    assert "ts_decay_linear(" in compiled


def test_generate_template_candidates():
    candidates = generate_template_candidates()
    assert len(candidates) > 0
    c0 = candidates[0]
    assert isinstance(c0, RiskModelCandidate)
    assert c0.universe in ("TOP3000", "TOP2000")
    assert c0.neutralization in ("SUBINDUSTRY", "SECTOR")
    assert "trade_when" in c0.expression or "group_neutralize" in c0.expression
