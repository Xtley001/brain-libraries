"""
Config loader for the Brain Alpha Engine.

All configuration is sourced **exclusively** from environment variables.
No hard-coded credentials, no config files, no defaults for secrets.

Environment variables (all optional — consuming packages validate as needed)
---------------------------------------------------------------------------
BRAIN_USERNAME               str   default=""
BRAIN_PASSWORD               str   default=""
BRAIN_MAX_CONCURRENT_SIMS    int   default=3
GROQ_API_KEY[_1..9]          str   default=[]
CEREBRAS_API_KEY[_1..9]      str   default=[]
OPENROUTER_API_KEY[_1..9]    str   default=[]
GEMINI_API_KEY[_1..9]        str   default=[]
TELEGRAM_BOT_TOKEN           str   default=None
TELEGRAM_CHAT_ID             str   default=None
DATABASE_URL                 str   default=None
STAGE0_MIN_SHARPE            float default=0.60
STAGE0_MIN_FITNESS           float default=0.50
FILTER_MIN_SHARPE            float default=1.25
FILTER_MIN_FITNESS           float default=1.00
FILTER_MIN_TURNOVER          float default=0.01
FILTER_MAX_TURNOVER          float default=0.70
MAX_POOL_CORRELATION         float default=0.70
UNIVERSE                     str   default="TOP3000"
DELAY                        int   default=1
MAX_CANDIDATES_PER_RUN       int   default=10
RUN_TIME_BUDGET_SECONDS      int   default=480
DRIP_MAX_DAILY               int   default=1
DRIP_MIN_INTERVAL_HOURS      float default=4.0
ENABLE_AUTO_SUBMIT           bool  default=False
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


class MissingConfigError(RuntimeError):
    """Raised when a required environment variable is absent or empty."""


def _optional(name: str, default: str | None = None) -> str | None:
    val = os.environ.get(name)
    if val is None or not val.strip():
        return default
    return val.strip()


@dataclass(frozen=True)
class Config:
    """Immutable, fully-typed view of the process environment."""

    # WorldQuant BRAIN credentials
    brain_username: str = ""
    brain_password: str = ""
    brain_max_concurrent_sims: int = 3

    # LLM API key pools
    groq_keys: list[str] = field(default_factory=list)
    cerebras_keys: list[str] = field(default_factory=list)
    openrouter_keys: list[str] = field(default_factory=list)
    gemini_keys: list[str] = field(default_factory=list)

    # Telegram notification
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Database
    database_url: str | None = None

    # Pipeline quality thresholds
    stage0_min_sharpe: float = 0.60
    stage0_min_fitness: float = 0.50
    filter_min_sharpe: float = 1.25
    filter_min_fitness: float = 1.00
    filter_min_turnover: float = 0.01
    filter_max_turnover: float = 0.70
    max_pool_correlation: float = 0.70

    # Operational settings
    universe: str = "TOP3000"
    delay: int = 1
    max_candidates_per_run: int = 10
    run_time_budget_seconds: int = 480
    drip_max_daily: int = 1
    drip_min_interval_hours: float = 4.0
    enable_auto_submit: bool = False

    @classmethod
    def load_from_env(cls, dotenv_path: str | None = None) -> "Config":
        """Build a frozen Config from the process environment (loads .env if dotenv_path provided)."""
        if dotenv_path is not None:
            load_dotenv(dotenv_path=dotenv_path)

        def _gather_keys(prefix: str) -> list[str]:
            """Collect base key + indexed variants KEY_1..KEY_9, de-duplicated."""
            keys: list[str] = []
            single = os.environ.get(prefix)
            if single and single.strip():
                keys.append(single.strip())
            for i in range(1, 10):
                k = os.environ.get(f"{prefix}_{i}")
                if k and k.strip() and k.strip() not in keys:
                    keys.append(k.strip())
            return keys

        return cls(
            brain_username=_optional("BRAIN_USERNAME", "") or "",
            brain_password=_optional("BRAIN_PASSWORD", "") or "",
            brain_max_concurrent_sims=int(_optional("BRAIN_MAX_CONCURRENT_SIMS", "3") or "3"),
            groq_keys=_gather_keys("GROQ_API_KEY"),
            cerebras_keys=_gather_keys("CEREBRAS_API_KEY"),
            openrouter_keys=_gather_keys("OPENROUTER_API_KEY"),
            gemini_keys=_gather_keys("GEMINI_API_KEY"),
            telegram_bot_token=_optional("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=_optional("TELEGRAM_CHAT_ID"),
            database_url=_optional("DATABASE_URL"),
            stage0_min_sharpe=float(_optional("STAGE0_MIN_SHARPE", "0.60") or "0.60"),
            stage0_min_fitness=float(_optional("STAGE0_MIN_FITNESS", "0.50") or "0.50"),
            filter_min_sharpe=float(_optional("FILTER_MIN_SHARPE", "1.25") or "1.25"),
            filter_min_fitness=float(_optional("FILTER_MIN_FITNESS", "1.00") or "1.00"),
            filter_min_turnover=float(_optional("FILTER_MIN_TURNOVER", "0.01") or "0.01"),
            filter_max_turnover=float(_optional("FILTER_MAX_TURNOVER", "0.70") or "0.70"),
            max_pool_correlation=float(_optional("MAX_POOL_CORRELATION", "0.70") or "0.70"),
            universe=_optional("UNIVERSE", "TOP3000") or "TOP3000",
            delay=int(_optional("DELAY", "1") or "1"),
            max_candidates_per_run=int(_optional("MAX_CANDIDATES_PER_RUN", "10") or "10"),
            run_time_budget_seconds=int(_optional("RUN_TIME_BUDGET_SECONDS", "480") or "480"),
            drip_max_daily=int(_optional("DRIP_MAX_DAILY", "1") or "1"),
            drip_min_interval_hours=float(_optional("DRIP_MIN_INTERVAL_HOURS", "4.0") or "4.0"),
            enable_auto_submit=(
                _optional("ENABLE_AUTO_SUBMIT", "false") or "false"
            ).lower() == "true",
        )
