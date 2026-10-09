"""
PostgreSQL adapter for brain_store.

DATABASE SCHEMA — 7 Tables
==========================
1. options_alphas          — Qualified alpha pool (status: QUALIFIED | SUBMITTED).
2. options_evaluations     — Immutable audit log of every simulation run.
3. options_learning_memory — MAB reinforcement-learning memory (one row per expression).
4. options_rejected_alphas — Alphas that failed BRAIN platform checklist gates.
5. options_correlated_alphas — Alphas that failed self-correlation < 0.70 gate.
6. cluster_session_cache   — Shared BRAIN session token cache across worker orgs.
7. cluster_run_lock        — Cluster-wide mutex: prevents > 1 org simulating at once.

All tables use IF NOT EXISTS — safe to run on first boot and on upgrades.

This module is extracted from brain_options/store/db.py.
It owns ALL DDL and DML. No other module may issue raw SQL.
"""
from __future__ import annotations

import json
import logging
import math
import re
import time
from typing import Any, Dict, List, Optional, Set

try:
    from psycopg_pool import ConnectionPool
except ImportError:
    ConnectionPool = None  # type: ignore[assignment,misc]

log = logging.getLogger("brain_store.db")

# ── Schema DDL ────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS options_alphas (
    id               SERIAL PRIMARY KEY,
    alpha_id         VARCHAR(64),
    expression       TEXT        NOT NULL,
    archetype        VARCHAR(128),
    hypothesis       TEXT,
    source           VARCHAR(32),
    sharpe           NUMERIC(8, 4),
    fitness          NUMERIC(8, 4),
    turnover         NUMERIC(8, 4),
    returns          NUMERIC(8, 4),
    drawdown         NUMERIC(8, 4),
    margin           NUMERIC(10, 6),
    max_correlation  NUMERIC(8, 4),
    universe         VARCHAR(32),
    neutralization   VARCHAR(32),
    delay            INTEGER,
    decay            INTEGER,
    truncation       NUMERIC(6, 4),
    pasteurization   VARCHAR(8),
    nan_handling     VARCHAR(8),
    status           VARCHAR(32) DEFAULT 'QUALIFIED',
    submitted_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS options_evaluations (
    id          SERIAL PRIMARY KEY,
    expression  TEXT        NOT NULL,
    archetype   VARCHAR(128),
    source      VARCHAR(32),
    stage       VARCHAR(32),
    status      VARCHAR(32),
    sharpe      NUMERIC(8, 4),
    fitness     NUMERIC(8, 4),
    turnover    NUMERIC(8, 4),
    returns     NUMERIC(8, 4),
    drawdown    NUMERIC(8, 4),
    alpha_id    VARCHAR(64),
    created_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS options_learning_memory (
    id             SERIAL PRIMARY KEY,
    expression     TEXT UNIQUE NOT NULL,
    reward_score   NUMERIC(10, 4) DEFAULT 0,
    sample_count   INTEGER DEFAULT 0,
    success_count  INTEGER DEFAULT 0,
    fail_count     INTEGER DEFAULT 0,
    last_updated   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS options_rejected_alphas (
    id          SERIAL PRIMARY KEY,
    expression  TEXT        NOT NULL,
    archetype   VARCHAR(128),
    sharpe      NUMERIC(8, 4),
    fitness     NUMERIC(8, 4),
    reason      TEXT,
    created_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS options_correlated_alphas (
    id               SERIAL PRIMARY KEY,
    expression       TEXT        NOT NULL,
    archetype        VARCHAR(128),
    sharpe           NUMERIC(8, 4),
    fitness          NUMERIC(8, 4),
    max_correlation  NUMERIC(8, 4),
    corr_partner_id  VARCHAR(64),
    created_at       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cluster_session_cache (
    org_id       VARCHAR(64) PRIMARY KEY,
    session_data TEXT        NOT NULL,
    updated_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cluster_run_lock (
    lock_key    VARCHAR(64) PRIMARY KEY,
    holder_org  VARCHAR(64),
    acquired_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
"""

# ── Database class ────────────────────────────────────────────────────────

class OptionsDatabase:
    """
    Low-level PostgreSQL adapter.

    Manages a psycopg_pool ConnectionPool and exposes typed read/write
    methods for every table. All raw SQL lives in this class.

    Parameters
    ----------
    database_url : PostgreSQL DSN, e.g. "postgresql://user:pass@host/db".
                   When None the pool is not created and all operations
                   are silently no-ops (file-only mode).
    pool_min     : Minimum pool connections (default 1).
    pool_max     : Maximum pool connections (default 5).
    """

    def __init__(
        self,
        database_url: Optional[str],
        pool_min: int = 1,
        pool_max: int = 5,
    ) -> None:
        self._pool: Optional[Any] = None
        if database_url and ConnectionPool is not None:
            try:
                self._pool = ConnectionPool(
                    database_url,
                    min_size=pool_min,
                    max_size=pool_max,
                    open=True,
                )
                self._init_schema()
                log.info("brain_store: PostgreSQL pool initialised (min=%d max=%d)", pool_min, pool_max)
            except Exception as exc:
                log.error("brain_store: Failed to connect to PostgreSQL: %s", exc)
                self._pool = None

    def is_available(self) -> bool:
        """Return True if a live PostgreSQL connection pool is available."""
        return self._pool is not None

    # ── Schema init ───────────────────────────────────────────────────────

    def _init_schema(self) -> None:
        """Create tables if they do not already exist."""
        if self._pool is None:
            return
        try:
            with self._pool.connection() as conn:
                conn.execute(SCHEMA_SQL)
                conn.commit()
            log.info("brain_store: Schema initialised.")
        except Exception as exc:
            log.warning("brain_store: Schema init error (may be benign on concurrent start): %s", exc)

    # ── Deduplication helpers ─────────────────────────────────────────────

    def load_evaluated_expressions(self) -> Set[str]:
        """Return the set of all expressions ever evaluated (from options_evaluations)."""
        if self._pool is None:
            return set()
        result: Set[str] = set()
        try:
            with self._pool.connection() as conn:
                rows = conn.execute("SELECT expression FROM options_evaluations").fetchall()
                for row in rows:
                    result.add(row[0])
        except Exception as exc:
            log.warning("brain_store: load_evaluated_expressions failed: %s", exc)
        return result

    # ── Alpha pool writes ─────────────────────────────────────────────────

    def save_qualified_alpha(self, record: Dict[str, Any]) -> None:
        """
        Insert one row into options_alphas (status=QUALIFIED).

        Parameters
        ----------
        record : dict with keys matching the options_alphas columns.
                 Required: expression (str).
                 Optional: alpha_id, archetype, hypothesis, source,
                           sharpe, fitness, turnover, returns, drawdown,
                           margin, max_correlation, universe,
                           neutralization, delay, decay, truncation,
                           pasteurization, nan_handling.
        """
        if self._pool is None:
            return
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    """
                    INSERT INTO options_alphas
                        (alpha_id, expression, archetype, hypothesis, source,
                         sharpe, fitness, turnover, returns, drawdown, margin,
                         max_correlation, universe, neutralization, delay, decay,
                         truncation, pasteurization, nan_handling, status)
                    VALUES
                        (%(alpha_id)s, %(expression)s, %(archetype)s,
                         %(hypothesis)s, %(source)s,
                         %(sharpe)s, %(fitness)s, %(turnover)s, %(returns)s,
                         %(drawdown)s, %(margin)s, %(max_correlation)s,
                         %(universe)s, %(neutralization)s, %(delay)s, %(decay)s,
                         %(truncation)s, %(pasteurization)s, %(nan_handling)s,
                         'QUALIFIED')
                    """,
                    record,
                )
                conn.commit()
        except Exception as exc:
            log.error("brain_store: save_qualified_alpha failed: %s", exc)

    def log_evaluation(self, record: Dict[str, Any]) -> None:
        """
        Append one row to options_evaluations (immutable audit log).

        Required keys: expression (str), stage (str), status (str).
        Optional keys: archetype, source, sharpe, fitness, turnover,
                       returns, drawdown, alpha_id.
        """
        if self._pool is None:
            return
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    """
                    INSERT INTO options_evaluations
                        (expression, archetype, source, stage, status,
                         sharpe, fitness, turnover, returns, drawdown, alpha_id)
                    VALUES
                        (%(expression)s, %(archetype)s, %(source)s,
                         %(stage)s, %(status)s,
                         %(sharpe)s, %(fitness)s, %(turnover)s,
                         %(returns)s, %(drawdown)s, %(alpha_id)s)
                    """,
                    record,
                )
                conn.commit()
        except Exception as exc:
            log.error("brain_store: log_evaluation failed: %s", exc)

    # ── MAB / RL state ────────────────────────────────────────────────────

    def upsert_rl_reward(self, expression: str, delta: float) -> None:
        """
        Add *delta* to the reward_score for *expression* in options_learning_memory.

        Uses ON CONFLICT DO UPDATE for idempotent upsert.
        Increments sample_count by 1 each call.
        Increments success_count if delta > 0, fail_count if delta < 0.
        """
        if self._pool is None:
            return
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    """
                    INSERT INTO options_learning_memory
                        (expression, reward_score, sample_count,
                         success_count, fail_count, last_updated)
                    VALUES
                        (%(expr)s, %(delta)s, 1,
                         CASE WHEN %(delta)s > 0 THEN 1 ELSE 0 END,
                         CASE WHEN %(delta)s < 0 THEN 1 ELSE 0 END,
                         CURRENT_TIMESTAMP)
                    ON CONFLICT (expression) DO UPDATE SET
                        reward_score  = options_learning_memory.reward_score + %(delta)s,
                        sample_count  = options_learning_memory.sample_count + 1,
                        success_count = options_learning_memory.success_count
                                      + CASE WHEN %(delta)s > 0 THEN 1 ELSE 0 END,
                        fail_count    = options_learning_memory.fail_count
                                      + CASE WHEN %(delta)s < 0 THEN 1 ELSE 0 END,
                        last_updated  = CURRENT_TIMESTAMP
                    """,
                    {"expr": expression, "delta": delta},
                )
                conn.commit()
        except Exception as exc:
            log.error("brain_store: upsert_rl_reward failed: %s", exc)

    def load_top_performing_exemplars(
        self,
        limit: int = 5,
        min_sharpe: float = 1.0,
        exclude_archetypes: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return up to *limit* rows from options_alphas ordered by sharpe DESC.

        Filters: sharpe >= min_sharpe, status IN ('QUALIFIED', 'SUBMITTED').
        Excludes rows whose archetype is in *exclude_archetypes* (if given).
        """
        if self._pool is None:
            return []
        try:
            excl = exclude_archetypes or []
            with self._pool.connection() as conn:
                rows = conn.execute(
                    """
                    SELECT expression, archetype, sharpe, fitness, turnover
                    FROM   options_alphas
                    WHERE  sharpe >= %(min_sharpe)s
                      AND  status IN ('QUALIFIED', 'SUBMITTED')
                      AND  (%(excl_len)s = 0 OR archetype != ALL(%(excl)s))
                    ORDER  BY sharpe DESC
                    LIMIT  %(limit)s
                    """,
                    {
                        "min_sharpe": min_sharpe,
                        "excl": excl,
                        "excl_len": len(excl),
                        "limit": limit,
                    },
                ).fetchall()
                return [
                    {"expression": r[0], "archetype": r[1],
                     "sharpe": float(r[2] or 0), "fitness": float(r[3] or 0),
                     "turnover": float(r[4] or 0)}
                    for r in rows
                ]
        except Exception as exc:
            log.warning("brain_store: load_top_performing_exemplars failed: %s", exc)
            return []

    def load_archetype_performance_summary(self) -> Dict[str, Any]:
        """
        Return a dict mapping archetype_name -> {win_rate, avg_sharpe, total_runs}.
        Computed from options_evaluations where status == 'PASS'.
        """
        if self._pool is None:
            return {}
        try:
            with self._pool.connection() as conn:
                rows = conn.execute(
                    """
                    SELECT
                        archetype,
                        COUNT(*)                                            AS total_runs,
                        COUNT(*) FILTER (WHERE status = 'PASS')            AS wins,
                        AVG(sharpe) FILTER (WHERE status = 'PASS')         AS avg_sharpe
                    FROM   options_evaluations
                    WHERE  archetype IS NOT NULL
                    GROUP  BY archetype
                    """
                ).fetchall()
            result: Dict[str, Any] = {}
            for row in rows:
                arch, total, wins, avg_sh = row
                result[arch] = {
                    "total_runs": int(total),
                    "win_rate": round(int(wins) / max(int(total), 1), 4),
                    "avg_sharpe": round(float(avg_sh or 0), 4),
                }
            return result
        except Exception as exc:
            log.warning("brain_store: load_archetype_performance_summary failed: %s", exc)
            return {}

    def save_correlated_alpha(self, record: Dict[str, Any]) -> None:
        """Insert one row into options_correlated_alphas."""
        if self._pool is None:
            return
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    """
                    INSERT INTO options_correlated_alphas
                        (expression, archetype, sharpe, fitness,
                         max_correlation, corr_partner_id)
                    VALUES
                        (%(expression)s, %(archetype)s, %(sharpe)s,
                         %(fitness)s, %(max_correlation)s, %(corr_partner_id)s)
                    """,
                    record,
                )
                conn.commit()
        except Exception as exc:
            log.error("brain_store: save_correlated_alpha failed: %s", exc)

    def save_rejected_alpha(self, record: Dict[str, Any]) -> None:
        """Insert one row into options_rejected_alphas."""
        if self._pool is None:
            return
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    """
                    INSERT INTO options_rejected_alphas
                        (expression, archetype, sharpe, fitness, reason)
                    VALUES
                        (%(expression)s, %(archetype)s, %(sharpe)s,
                         %(fitness)s, %(reason)s)
                    """,
                    record,
                )
                conn.commit()
        except Exception as exc:
            log.error("brain_store: save_rejected_alpha failed: %s", exc)

    def close(self) -> None:
        """Close the connection pool gracefully."""
        if self._pool is not None:
            try:
                self._pool.close()
            except Exception:
                pass


def map_archetype_to_core(archetype_name: str) -> str:
    """
    Normalises arbitrary archetype labels (from LLM output, mutation tags, etc.)
    to the canonical 30-strategy taxonomy.
    """
    if not archetype_name:
        return "forward_basis"
    name = archetype_name.lower().strip()

    if "dynamic_short_squeeze" in name or "dynamic short squeeze" in name or "borrow fee convexity" in name:
        return "dynamic_short_squeeze"
    elif "days_to_cover" in name or "days-to-cover" in name or "days to cover" in name:
        return "short_interest"
    elif "vpin" in name or "toxicity" in name or "order_flow" in name:
        return "order_flow_vpin"
    elif "gamma" in name or "pinning" in name:
        return "gamma_pinning_clustering"
    elif "customer" in name or "cascades" in name or "customer_supplier" in name:
        return "customer_supplier_cascades"
    elif "rd_" in name or "r&d" in name or "spillover" in name:
        return "rd_capitalization_spillovers"
    elif "capex" in name or "asset_growth" in name or "asset growth" in name:
        return "capex_asset_growth"
    elif "peavrp" in name or "vrp compression" in name or "vrp crush" in name:
        return "peavrp_volatility_premia"
    elif "jump" in name or "realized_jump" in name:
        return "realized_jump_intensity"
    elif "default" in name or "merton" in name or "distance_to_default" in name:
        return "distance_to_default_debt"
    elif "macro" in name or "fomc" in name or "cpi" in name:
        return "macro_fomc_cpi_drift"
    elif "patent" in name or "innovation" in name:
        return "patent_innovation_efficiency"
    elif "peavd" in name:
        return "peavd_earnings_vol_drift"
    elif "insider" in name or "cluster" in name:
        return "insider_cluster_buying"
    elif "13f" in name or "institutional" in name or "breadth" in name:
        return "institutional_13f_breadth"
    elif "supply_chain" in name or "supply chain" in name:
        return "supply_chain"
    elif "informed_short" in name or "informed short" in name:
        return "informed_short_demand"
    elif "extreme_tail" in name or "tail_risk" in name or "extreme tail" in name:
        return "extreme_tail_risk"
    elif "iv_lead" in name or "lead_lag" in name or "lead lag" in name:
        return "iv_lead_lag"
    elif "network_momentum" in name or "network momentum" in name:
        return "network_momentum"
    elif "accruals" in name or "sloan" in name or "cashflow" in name:
        return "accruals_cashflow"
    elif "formulaic" in name or "101" in name or "kakushadze" in name:
        return "formulaic_101"
    elif "hybrid" in name or "confluence" in name or "divergence" in name:
        return "hybrid_confluence"
    elif "breakeven" in name:
        return "breakeven"
    elif "skew" in name or "smirk" in name:
        return "skew"
    elif "term_structure" in name or "term structure" in name or "vrp" in name or "variance" in name or "parkinson" in name:
        return "term_structure"
    elif "forward" in name or "basis" in name:
        return "forward_basis"
    elif "pcr" in name or "put-call" in name or "put_call" in name or "flow" in name:
        return "pcr_flow"
    elif "analyst" in name or "revision" in name or "dispersion" in name or "pead" in name or "target_price" in name or "price target" in name or "sales" in name:
        return "analyst_revisions"
    elif "short" in name or "borrow" in name or "days_to_cover" in name:
        return "short_interest"
    return name

