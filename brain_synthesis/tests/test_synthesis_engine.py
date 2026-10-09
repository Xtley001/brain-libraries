"""
Unit tests — brain_synthesis.engine and combiner
"""
from brain_core.types import AlphaCandidate
from brain_synthesis.engine import SynthesisEngine
from brain_synthesis.combiner import DynamicSynthesizer


def test_dynamic_synthesizer_single_and_multi_leg():
    syn = DynamicSynthesizer()
    leg1 = AlphaCandidate(expression="rank(close)", archetype_name="opt_leg")
    leg2 = AlphaCandidate(expression="snt1_d1_netearningsrevision", archetype_name="snt_leg")

    res = syn.synthesize([(leg1, 0.6), (leg2, 0.4)], name="Custom_Synthesis")
    assert res.archetype_name == "Custom_Synthesis"
    assert "group_neutralize(" in res.expression
    assert "0.60 * rank(close)" in res.expression
    assert "0.40 * rank(snt1_d1_netearningsrevision)" in res.expression


def test_synthesis_engine_decorrelation():
    engine = SynthesisEngine()
    golden = engine.get_golden_candidates()
    assert len(golden) > 0

    c0 = golden[0]
    variants = engine.decorrelate_candidate(c0, base_sharpe=1.55)
    assert isinstance(variants, list)
    assert len(variants) > 0


def test_synthesis_engine_domain_generation():
    engine = SynthesisEngine()
    dom_cands = engine.generate_domain_candidates(count=1)
    assert "options" in dom_cands
    assert "sentiment" in dom_cands
    assert "risk_model" in dom_cands


def test_synthesis_cli_parser():
    from brain_synthesis.cli import build_parser, main
    parser = build_parser()
    args = parser.parse_args(["generate", "--domain", "synthesis", "--count", "1", "--json"])
    assert args.domain == "synthesis"
    assert args.count == 1
    assert args.json is True

    # Test main execution of CLI
    res = main(["generate", "--domain", "synthesis", "--count", "1"])
    assert res == 0
