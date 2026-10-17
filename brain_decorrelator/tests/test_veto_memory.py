"""
Unit tests for brain_decorrelator.veto_memory
"""
from brain_decorrelator.veto_memory.store import VetoMemory
from brain_decorrelator.veto_memory.veto_gate import VetoGate


def test_veto_memory_record_and_check():
    mem = VetoMemory()
    motif = "ts_decay_linear(ts_delta)"
    assert not mem.is_vetoed(motif, universe="TOP3000")

    # Record collision with high correlation (>= 0.70)
    mem.record_collision(motif, colliding_alpha_id="alpha_123", correlation_score=0.88, universe="TOP3000")
    assert mem.is_vetoed(motif, universe="TOP3000")
    assert not mem.is_vetoed(motif, universe="TOP1000")  # Different universe not vetoed


def test_veto_gate_filters_candidates():
    mem = VetoMemory()
    # Veto ts_decay_linear calls with identifier
    mem.record_collision("ts_decay_linear(identifier,literal)", "alpha_999", 0.92, universe="TOP3000")
    gate = VetoGate(mem)

    candidates = [
        "ts_decay_linear(close, 10)",
        "group_neutralize(rank(close), subindustry)",
    ]

    filtered = gate.filter_candidates(candidates, universe="TOP3000")
    assert len(filtered) == 1
    assert "group_neutralize" in filtered[0]
