# brain-store

Dual-mode persistence layer (PostgreSQL connection pool + flat-file fallback) and RL state store for Brain Alpha pipelines.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-libraries/ci.yml?branch=main)](https://github.com/Xtley001/brain-libraries/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-store)](https://pypi.org/project/brain-store/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_store` provides resilient, dual-mode persistence for quantitative alpha pipelines. It connects to Neon PostgreSQL with connection pooling via `psycopg_pool` while falling back automatically to local zero-config JSON/CSV file storage when `DATABASE_URL` is absent. For the complete relational entity-relationship diagram and database migration operations, see [Schema & Migrations](./docs/SCHEMA_AND_MIGRATIONS.md).

## Installation

```bash
pip install brain-store
```

## Quickstart

```python
from brain_store import AlphaStore

# Connects to PostgreSQL if DATABASE_URL is set, otherwise uses ./data/
store = AlphaStore(data_dir="./data")

# Save a qualified alpha
store.save_qualified_alpha({
    "expression": "group_neutralize(rank(close), subindustry)",
    "sharpe": 1.85,
    "fitness": 1.42,
})

# Load historical expressions with pagination to prevent OOM
evaluated = store.load_evaluated_expressions(limit=500, offset=0)
print(f"Loaded {len(evaluated)} evaluated expressions.")
```

> **Note:** `OptionsStore` is preserved as a backward-compatible alias for `AlphaStore`.

## Architecture

```
brain_store/
├── brain_store/
│   ├── __init__.py        # Public re-exports (AlphaStore, OptionsStore, OptionsDatabase)
│   ├── db.py              # OptionsDatabase — connection pool, 9-table DDL, RL state
│   ├── store.py           # AlphaStore — high-level dual-mode facade
│   ├── py.typed           # PEP 561 typing marker
│   └── migrations/        # DDL migration scripts
├── tests/                 # Offline unit tests (no PostgreSQL instance required)
└── docs/
    ├── API.md             # Complete API specification
    └── SCHEMA_AND_MIGRATIONS.md # Relational schema diagram & migration runbook
```

## Database Schema

| Table | Purpose | Indexing Strategy |
|---|---|---|
| `options_alphas` | Live alpha reserve vault | Unique on `alpha_id`, Index on `status`, `category` |
| `options_evaluations` | Simulation backtest audit log | Index on `alpha_id`, `simulated_at` |
| `options_strategy_rl_state` | Strategy-level reinforcement learning operator weights | Primary key on `strategy_name` |
| `options_learning_memory` | Global Multi-Armed Bandit expression reward tracking | Primary key on `expression_hash` |
| `options_rejected_alphas` | Diagnostics for checklist / gate-failed alphas | Index on `failure_reason` |
| `options_correlated_alphas` | Audit log of correlation gate rejections (|rho| >= 0.70) | Index on `candidate_id` |
| `cluster_session_cache` | Distributed BRAIN auth session token caching (2h TTL) | Primary key on `session_key` |
| `cluster_run_lock` | Distributed mutex preventing duplicate simulation runs | Primary key on `lock_name` |
| `org_runs` | Runner heartbeat and telemetry monitoring | Primary key on `run_id` |

## Testing

```bash
pytest tests/ -v
```

Tests run offline without requiring a live PostgreSQL instance.

## Security

Report vulnerabilities per [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

Released under the [MIT License](../LICENSE). Maintained by [Xtley001](https://github.com/Xtley001).
