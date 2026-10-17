"""
Asymmetric Veto Memory & Collision Store.
Implements the Veto Control mechanism from AlphaMemo (Yu et al., 2026).
Caches high-correlation collision patterns to proactively suppress redundant mutations.
"""
from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

log = logging.getLogger("brain_decorrelator.veto_memory")


@dataclass(frozen=True)
class CollisionRecord:
    """Record of a failed candidate that breached the correlation gate."""
    motif_signature: str
    colliding_alpha_id: str
    correlation_score: float
    universe: str
    timestamp: float = 0.0


class VetoMemory:
    """
    Tracks historical alpha collisions and applies asymmetric veto control
    to suppress candidate motifs that repeatedly collide with portfolio alphas.
    """

    def __init__(self, db_path: Optional[str] = None):
        self._in_memory_records: List[CollisionRecord] = []
        self._vetoed_motifs: Dict[str, Set[str]] = {}  # universe -> set of motif_signatures
        self.db_path = db_path
        if self.db_path:
            self._init_sqlite()

    def _init_sqlite(self) -> None:
        """Initializes SQLite collision table if db_path is provided."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS collision_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        motif_signature TEXT NOT NULL,
                        colliding_alpha_id TEXT NOT NULL,
                        correlation_score REAL NOT NULL,
                        universe TEXT NOT NULL,
                        timestamp REAL NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as e:
            log.warning("VetoMemory: Failed to initialize SQLite storage: %s", e)

    def record_collision(
        self,
        motif_signature: str,
        colliding_alpha_id: str,
        correlation_score: float,
        universe: str = "TOP3000",
        threshold: float = 0.70,
    ) -> None:
        """
        Record a collision event. If correlation_score >= threshold, the motif is vetoed.
        """
        now = time.time()
        record = CollisionRecord(
            motif_signature=motif_signature,
            colliding_alpha_id=colliding_alpha_id,
            correlation_score=correlation_score,
            universe=universe,
            timestamp=now,
        )
        self._in_memory_records.append(record)

        if correlation_score >= threshold:
            if universe not in self._vetoed_motifs:
                self._vetoed_motifs[universe] = set()
            self._vetoed_motifs[universe].add(motif_signature)

        if self.db_path:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO collision_records
                        (motif_signature, colliding_alpha_id, correlation_score, universe, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (motif_signature, colliding_alpha_id, correlation_score, universe, now),
                    )
                    conn.commit()
            except Exception as e:
                log.warning("VetoMemory: SQLite record write failed: %s", e)

    def is_vetoed(self, motif_signature: str, universe: str = "TOP3000") -> bool:
        """Returns True if the motif signature is in the active veto set for the specified universe."""
        vetoed_set = self._vetoed_motifs.get(universe, set())
        return motif_signature in vetoed_set

    def get_records(self, universe: Optional[str] = None) -> List[CollisionRecord]:
        """Returns all in-memory collision records, optionally filtered by universe."""
        if universe:
            return [r for r in self._in_memory_records if r.universe == universe]
        return list(self._in_memory_records)

    def clear(self) -> None:
        """Clears in-memory cache."""
        self._in_memory_records.clear()
        self._vetoed_motifs.clear()
