"""Unit tests — brain_core.types"""
from brain_core.types import SimSettings, SimMetrics, AlphaCandidate


def test_sim_settings_payload_structure():
    s = SimSettings()
    p = s.to_simulation_payload("rank(close)")
    assert p["regular"] == "rank(close)"
    assert p["settings"]["universe"] == "TOP3000"
    assert p["settings"]["pasteurization"] == "ON"
    assert p["settings"]["nanHandling"] == "OFF"
    assert p["settings"]["language"] == "FASTEXPR"


def test_sim_metrics_is_valid_on_complete():
    m = SimMetrics(status="COMPLETE", sharpe=1.3, fitness=1.1)
    assert m.is_valid is True


def test_sim_metrics_is_valid_fallback():
    # Provider returned unknown status but real non-zero metrics.
    m = SimMetrics(status="UNKNOWN", sharpe=1.3, fitness=0.0)
    assert m.is_valid is True


def test_sim_metrics_is_invalid():
    m = SimMetrics(status="ERROR", sharpe=0.0, fitness=0.0)
    assert m.is_valid is False


def test_sim_metrics_passed_stage0():
    m = SimMetrics(status="COMPLETE", sharpe=0.8, fitness=0.6)
    assert m.passed_stage0(min_sharpe=0.60, min_fitness=0.50) is True
    assert m.passed_stage0(min_sharpe=1.25, min_fitness=1.00) is False


def test_alpha_candidate_defaults():
    cand = AlphaCandidate(expression="rank(close)", archetype_name="Momentum")
    assert cand.generation_source == "template"
    assert cand.base_alpha_id is None
    assert cand.operator_name is None


def test_alpha_candidate_generation_source_validation():
    import pytest
    cand = AlphaCandidate(expression="rank(close)", archetype_name="Momentum", generation_source="synthesis")
    assert cand.generation_source == "synthesis"

    with pytest.raises(ValueError, match="Invalid generation_source"):
        AlphaCandidate(expression="rank(close)", archetype_name="Momentum", generation_source="unsupported_source_xyz")
