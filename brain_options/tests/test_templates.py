"""
Unit tests — brain_options.templates
"""
from brain_options.templates import (
    OptionCandidate,
    compile_fitness_invariant,
    generate_template_candidates,
)


def test_compile_fitness_invariant():
    expr = "forward_price_30 - put_breakeven_30"
    compiled = compile_fitness_invariant(expr)
    assert "group_neutralize(" in compiled or "trade_when(" in compiled


def test_generate_template_candidates():
    cands = generate_template_candidates()
    assert len(cands) > 0
    c0 = cands[0]
    assert isinstance(c0, OptionCandidate)
    assert c0.expression
    assert c0.universe in ("TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500")
