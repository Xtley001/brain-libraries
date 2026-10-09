"""
brain_store — persistence layer for the Brain Alpha Engine.

Public API
----------
OptionsDatabase  : PostgreSQL adapter. Owns all DDL, DML, and RL state ops.
AlphaStore       : High-level store facade combining CSV/JSON + Postgres.
OptionsStore     : Deprecated alias for AlphaStore (backwards-compatibility).
"""
from brain_store.db import OptionsDatabase, map_archetype_to_core
from brain_store.store import AlphaStore, OptionsStore

__all__ = [
    "OptionsDatabase",
    "map_archetype_to_core",
    "AlphaStore",
    "OptionsStore",
]
