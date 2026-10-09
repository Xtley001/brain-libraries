"""
Unit tests for brain_store.store.OptionsStore — file-only mode (no Postgres).

Uses a tmp_path fixture so no real CSV/JSON files are created in the repo.

Acceptance criteria
-------------------
AC-1  save_qualified_alpha() creates passed_options_alphas.csv.
AC-2  log_evaluation() creates evaluated_candidates.csv.
AC-3  load_evaluated_expressions() returns expressions from the CSV.
AC-4  cache_pnl/load_pnl round-trip works correctly.
"""
import os
import pytest
from brain_store.store import OptionsStore


@pytest.fixture
def store(tmp_path):
    return OptionsStore(data_dir=str(tmp_path), database_url=None)


def test_ac1_save_qualified_alpha(store, tmp_path):
    store.save_qualified_alpha({"expression": "rank(close)", "sharpe": 1.5, "fitness": 1.1})
    assert os.path.exists(os.path.join(str(tmp_path), "passed_options_alphas.csv"))


def test_ac2_log_evaluation(store, tmp_path):
    store.log_evaluation({"expression": "rank(close)", "stage": "STAGE0", "status": "PASS"})
    assert os.path.exists(os.path.join(str(tmp_path), "evaluated_candidates.csv"))


def test_ac3_load_evaluated_expressions(store):
    store.log_evaluation({"expression": "rank(close)", "stage": "STAGE0", "status": "PASS"})
    store.log_evaluation({"expression": "rank(volume)", "stage": "STAGE0", "status": "FAIL"})
    exprs = store.load_evaluated_expressions()
    assert "rank(close)" in exprs
    assert "rank(volume)" in exprs


def test_ac4_pnl_cache_round_trip(store):
    pnl = [0.01, -0.02, 0.03]
    store.cache_pnl("test_alpha_001", pnl)
    loaded = store.load_pnl("test_alpha_001")
    assert loaded == pnl


def test_load_pnl_missing_returns_none(store):
    assert store.load_pnl("nonexistent_id") is None


def test_alphastore_alias_and_repr(tmp_path):
    from brain_store import AlphaStore, OptionsStore
    assert AlphaStore is OptionsStore
    s = AlphaStore(data_dir=str(tmp_path), database_url=None)
    assert repr(s).startswith("AlphaStore(")
    assert s.db.is_available() is False


def test_load_evaluated_expressions_pagination(store):
    store.log_evaluation({"expression": "expr_1", "stage": "STAGE0", "status": "PASS"})
    store.log_evaluation({"expression": "expr_2", "stage": "STAGE0", "status": "PASS"})
    store.log_evaluation({"expression": "expr_3", "stage": "STAGE0", "status": "PASS"})
    page = store.load_evaluated_expressions(limit=2, offset=0)
    assert len(page) == 2
