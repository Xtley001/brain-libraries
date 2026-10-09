"""
Unit tests — brain_core.config.Config.load_from_env()

Acceptance criteria
-------------------
AC-1  load_from_env() returns a frozen Config instance.
AC-2  Numeric env vars are parsed to the declared Python type.
AC-3  ENABLE_AUTO_SUBMIT='true' (any case) sets enable_auto_submit=True.
AC-4  Multi-key gathering merges GROQ_API_KEY, GROQ_API_KEY_1, GROQ_API_KEY_2.
AC-5  Duplicate key values are de-duplicated.
AC-6  Attempting to mutate a Config field raises an exception.
"""
import os
import pytest
from brain_core.config import Config


@pytest.fixture(autouse=True)
def clean_config_env(monkeypatch):
    """Ensure complete environment isolation for every test."""
    prefixes = [
        "GROQ_API_KEY",
        "CEREBRAS_API_KEY",
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
    ]
    for prefix in prefixes:
        monkeypatch.delenv(prefix, raising=False)
        for i in range(1, 10):
            monkeypatch.delenv(f"{prefix}_{i}", raising=False)

    standard_keys = [
        "BRAIN_USERNAME",
        "BRAIN_PASSWORD",
        "BRAIN_MAX_CONCURRENT_SIMS",
        "DATABASE_URL",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "STAGE0_MIN_SHARPE",
        "STAGE0_MIN_FITNESS",
        "FILTER_MIN_SHARPE",
        "FILTER_MIN_FITNESS",
        "FILTER_MIN_TURNOVER",
        "FILTER_MAX_TURNOVER",
        "MAX_POOL_CORRELATION",
        "ENABLE_AUTO_SUBMIT",
        "UNIVERSE",
        "DELAY",
        "MAX_CANDIDATES_PER_RUN",
        "RUN_TIME_BUDGET_SECONDS",
        "DRIP_MAX_DAILY",
        "DRIP_MIN_INTERVAL_HOURS",
    ]
    for key in standard_keys:
        monkeypatch.delenv(key, raising=False)


def test_ac1_defaults():
    cfg = Config.load_from_env()
    assert isinstance(cfg, Config)
    assert cfg.brain_username == ""
    assert cfg.stage0_min_sharpe == 0.60
    assert cfg.filter_min_sharpe == 1.25
    assert cfg.universe == "TOP3000"
    assert cfg.delay == 1
    assert cfg.enable_auto_submit is False
    assert cfg.groq_keys == []
    assert cfg.cerebras_keys == []
    assert cfg.openrouter_keys == []
    assert cfg.gemini_keys == []


def test_ac2_numeric_parsing(monkeypatch):
    monkeypatch.setenv("DELAY", "5")
    monkeypatch.setenv("STAGE0_MIN_SHARPE", "1.15")
    monkeypatch.setenv("BRAIN_MAX_CONCURRENT_SIMS", "7")
    cfg = Config.load_from_env()
    assert cfg.delay == 5
    assert cfg.stage0_min_sharpe == 1.15
    assert cfg.brain_max_concurrent_sims == 7


def test_ac3_enable_auto_submit_true(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTO_SUBMIT", "TRUE")
    cfg = Config.load_from_env()
    assert cfg.enable_auto_submit is True

    monkeypatch.setenv("ENABLE_AUTO_SUBMIT", "true")
    cfg = Config.load_from_env()
    assert cfg.enable_auto_submit is True

    monkeypatch.setenv("ENABLE_AUTO_SUBMIT", "0")
    cfg = Config.load_from_env()
    assert cfg.enable_auto_submit is False


def test_ac4_ac5_multi_key_gathering(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "key_base")
    monkeypatch.setenv("GROQ_API_KEY_1", "key_1")
    monkeypatch.setenv("GROQ_API_KEY_2", "key_base")  # duplicate — must be dropped
    cfg = Config.load_from_env()
    assert cfg.groq_keys == ["key_base", "key_1"]


def test_ac6_frozen():
    cfg = Config.load_from_env()
    with pytest.raises(Exception):
        cfg.delay = 99  # type: ignore[misc]
