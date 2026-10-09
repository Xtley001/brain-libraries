"""
OptionsStore — high-level facade over OptionsDatabase + flat-file storage.

Combines Postgres (via OptionsDatabase) with local CSV/JSON flat files so
the pipeline can survive without a database connection (file-only mode).

CSV/JSON files written
----------------------
passed_options_alphas.csv   — all qualified alphas (append-only)
passed_options_alphas.json  — same data in JSON (overwritten on each save)
rejected_options_alphas.csv — all rejected alphas
correlated_options_alphas.csv — all correlated alphas
evaluated_candidates.csv    — full evaluation history
pnl_series/<alpha_id>.json  — cached PnL vectors for correlation checks
"""
from __future__ import annotations

import csv
import json
import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from brain_store.db import OptionsDatabase

log = logging.getLogger("brain_store.store")

_SENTINEL = object()

_PASSED_CSV_HEADER = [
    "expression", "archetype", "hypothesis", "source",
    "sharpe", "fitness", "turnover", "returns", "drawdown",
    "margin", "universe", "neutralization", "delay", "decay",
    "truncation", "pasteurization", "nan_handling",
    "alpha_id", "status", "created_at",
]

_HISTORY_CSV_HEADER = [
    "expression", "archetype", "source", "stage", "status",
    "sharpe", "fitness", "turnover", "returns", "drawdown",
    "alpha_id", "created_at",
]


class AlphaStore:
    """
    High-level store facade.

    Parameters
    ----------
    data_dir     : Directory for CSV/JSON files.
                   Defaults to <package_root>/data.
    database_url : PostgreSQL DSN. Pass None to disable Postgres.
                   Defaults to DATABASE_URL env var.
    """

    def __init__(
        self,
        data_dir: Optional[str] = None,
        database_url: Any = _SENTINEL,
    ) -> None:
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
            )
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.passed_csv = os.path.join(self.data_dir, "passed_options_alphas.csv")
        self.passed_json = os.path.join(self.data_dir, "passed_options_alphas.json")
        self.rejected_csv = os.path.join(self.data_dir, "rejected_options_alphas.csv")
        self.correlated_csv = os.path.join(self.data_dir, "correlated_options_alphas.csv")
        self.history_csv = os.path.join(self.data_dir, "evaluated_candidates.csv")
        self.pnl_cache_dir = os.path.join(self.data_dir, "pnl_series")
        os.makedirs(self.pnl_cache_dir, exist_ok=True)

        if database_url is _SENTINEL:
            database_url = os.getenv("DATABASE_URL")

        self.db = OptionsDatabase(database_url)
        self._write_lock = threading.Lock()

    def __repr__(self) -> str:
        return f"AlphaStore(data_dir={self.data_dir!r}, postgres_enabled={self.db.is_available()})"

    # ── Deduplication ─────────────────────────────────────────────────────

    def load_evaluated_expressions(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Set[str]:
        """Return the set of all expressions previously evaluated, with optional limit/offset pagination."""
        evaluated: Set[str] = set()
        if os.path.exists(self.history_csv):
            try:
                with open(self.history_csv, "r", encoding="utf-8") as f:
                    count = 0
                    for idx, row in enumerate(csv.DictReader(f)):
                        if idx < offset:
                            continue
                        if limit is not None and count >= limit:
                            break
                        expr = row.get("expression")
                        if expr:
                            evaluated.add(expr.strip())
                            count += 1
            except Exception as exc:
                log.warning("Could not read evaluated history CSV: %s", exc)
        try:
            evaluated.update(self.db.load_evaluated_expressions())
        except Exception as exc:
            log.warning("Could not read evaluated expressions from DB: %s", exc)
        return evaluated

    # ── Qualified alpha writes ────────────────────────────────────────────

    def save_qualified_alpha(self, record: Dict[str, Any]) -> None:
        """
        Persist a qualified alpha to both CSV/JSON and Postgres.

        *record* must contain 'expression'. All other fields are optional.
        """
        record.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        record.setdefault("status", "QUALIFIED")
        with self._write_lock:
            self._append_csv(self.passed_csv, _PASSED_CSV_HEADER, record)
            self._rewrite_json(self.passed_csv, self.passed_json, _PASSED_CSV_HEADER)
        self.db.save_qualified_alpha(record)

    # ── Evaluation log ────────────────────────────────────────────────────

    def log_evaluation(self, record: Dict[str, Any]) -> None:
        """Append a simulation result to the evaluation history."""
        record.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        with self._write_lock:
            self._append_csv(self.history_csv, _HISTORY_CSV_HEADER, record)
        self.db.log_evaluation(record)

    # ── Top-performing exemplars ──────────────────────────────────────────

    def load_top_performing_exemplars(
        self,
        limit: int = 5,
        min_sharpe: float = 1.0,
        exclude_archetypes: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Return up to *limit* best-performing alphas from Postgres."""
        return self.db.load_top_performing_exemplars(
            limit=limit,
            min_sharpe=min_sharpe,
            exclude_archetypes=exclude_archetypes,
        )

    def load_archetype_performance_summary(self) -> Dict[str, Any]:
        """Return win rates and avg Sharpe per archetype from Postgres."""
        return self.db.load_archetype_performance_summary()

    # ── PnL cache ─────────────────────────────────────────────────────────

    def cache_pnl(self, alpha_id: str, pnl: List[float]) -> None:
        """Write *pnl* list to pnl_series/<alpha_id>.json."""
        path = os.path.join(self.pnl_cache_dir, f"{alpha_id}.json")
        with self._write_lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(pnl, f)

    def load_pnl(self, alpha_id: str) -> Optional[List[float]]:
        """Return cached PnL list or None if not present."""
        path = os.path.join(self.pnl_cache_dir, f"{alpha_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── Private helpers ───────────────────────────────────────────────────

    def _append_csv(
        self, path: str, header: List[str], record: Dict[str, Any]
    ) -> None:
        write_header = not os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
            if write_header:
                writer.writeheader()
            writer.writerow(record)

    def _rewrite_json(
        self, csv_path: str, json_path: str, header: List[str]
    ) -> None:
        rows: List[Dict[str, Any]] = []
        if os.path.exists(csv_path):
            with open(csv_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)


# Backwards-compatibility alias (deprecated in favor of AlphaStore)
OptionsStore = AlphaStore
