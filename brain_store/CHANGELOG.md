# Changelog — brain-store

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-10-09

### Added
- `AlphaStore` unified persistence facade with automated fallback between PostgreSQL and local JSON/CSV files.
- `OptionsStore` backward-compatible deprecated alias for `AlphaStore`.
- `OptionsDatabase` with 9-table schema and connection pooling via `psycopg_pool`.
- Added `is_available()` health check method for lazy database status verification.
- Pagination support (`limit`, `offset`) on `load_evaluated_expressions()`.
- Added clear `__repr__` for `AlphaStore` for enhanced developer ergonomics.
- MAB reinforcement learning memory state persistence (`upsert_rl_reward`).
- Distributed concurrency primitives: `cluster_run_lock` and `cluster_session_cache`.
- PEP 561 compliance marker (`py.typed`).
- PyPI packaging manifest with complete keywords and classifiers.
- Offline unit tests for both file-backed and simulated PostgreSQL connection failure modes.
