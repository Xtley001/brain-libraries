"""
Unit tests for brain_store.db — offline (no PostgreSQL required).

All tests use database_url=None so no real connection is made.
Acceptance criteria: all methods must be no-ops and not raise when pool=None.
"""
from brain_store.db import OptionsDatabase


def make_db() -> OptionsDatabase:
    return OptionsDatabase(database_url=None)


def test_load_evaluated_expressions_offline():
    db = make_db()
    result = db.load_evaluated_expressions()
    assert result == set()


def test_save_qualified_alpha_offline():
    db = make_db()
    db.save_qualified_alpha({"expression": "rank(close)", "sharpe": 1.5})
    # No exception expected


def test_log_evaluation_offline():
    db = make_db()
    db.log_evaluation({"expression": "rank(close)", "stage": "STAGE0", "status": "PASS"})


def test_upsert_rl_reward_offline():
    db = make_db()
    db.upsert_rl_reward("rank(close)", delta=10.0)


def test_load_top_performing_exemplars_offline():
    db = make_db()
    assert db.load_top_performing_exemplars() == []


def test_load_archetype_performance_summary_offline():
    db = make_db()
    assert db.load_archetype_performance_summary() == {}


def test_save_correlated_alpha_offline():
    db = make_db()
    db.save_correlated_alpha({"expression": "rank(close)", "max_correlation": 0.85})


def test_save_rejected_alpha_offline():
    db = make_db()
    db.save_rejected_alpha({"expression": "rank(close)", "reason": "low sharpe"})
