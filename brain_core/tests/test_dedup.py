"""Unit tests — brain_core.utils.dedup.ASTDeduplicator"""
from brain_core.utils.dedup import ASTDeduplicator


def test_ast_deduplicator_identical_formulas():
    dedup = ASTDeduplicator()
    assert dedup.add("rank(close)") is True
    assert dedup.is_duplicate("rank(close)") is True
    assert dedup.add("rank(close)") is False
    assert len(dedup) == 1


def test_ast_deduplicator_constant_normalization():
    dedup = ASTDeduplicator()
    assert dedup.add("ts_decay_linear(close, 5)") is True
    # Lookback 6 is in the same fast bucket (<= 8 -> 5)
    assert dedup.is_duplicate("ts_decay_linear(close, 6)") is True


def test_ast_deduplicator_commutative_invariance():
    dedup = ASTDeduplicator()
    assert dedup.add("close + open") is True
    assert dedup.is_duplicate("open + close") is True


def test_ast_deduplicator_populate():
    dedup = ASTDeduplicator()
    count = dedup.populate(["rank(close)", "rank(volume)", "rank(close)"])
    assert count == 2
    assert len(dedup) == 2
