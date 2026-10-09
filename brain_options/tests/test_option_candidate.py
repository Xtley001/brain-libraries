"""Unit tests — brain_options.generation.templates.OptionCandidate"""
from brain_options.generation.templates import OptionCandidate


def test_defaults():
    c = OptionCandidate(expression="rank(close)", archetype_name="Momentum")
    assert c.universe == "TOP3000"
    assert c.delay == 1
    assert c.decay == 8
    assert c.pasteurization is True


def test_override():
    c = OptionCandidate(
        expression="rank(close)",
        archetype_name="Skew",
        universe="TOP2000",
        delay=0,
    )
    assert c.universe == "TOP2000"
    assert c.delay == 0
