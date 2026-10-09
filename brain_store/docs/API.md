# brain-store API Reference

Dual-mode persistence engine supporting production PostgreSQL connection pools and zero-dependency local file caching.

## `OptionsStore`

Facade managing high-level alpha persistence and local PnL caching.

```python
from brain_store import OptionsStore

store = OptionsStore(data_dir="data", database_url=None)

# 1. Record qualified alpha
store.save_qualified_alpha({
    "alpha_id": "ALPH_101",
    "expression": "rank(forward_price_30 - put_breakeven_30)",
    "archetype": "breakeven",
    "sharpe": 1.65,
    "fitness": 1.20,
    "turnover": 0.12,
})

# 2. Query evaluated expressions for deduplication
known = store.load_evaluated_expressions()
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `save_qualified_alpha` | `(record: dict) -> None` | Writes alpha record to DB and local CSV |
| `log_evaluation` | `(record: dict) -> None` | Appends simulation telemetry to log |
| `load_evaluated_expressions` | `() -> set[str]` | Returns set of known expression strings |
| `cache_pnl` | `(alpha_id: str, pnl_series: list[float]) -> None` | Stores PnL vectors for correlation checks |
| `load_pnl` | `(alpha_id: str) -> list[float] \| None` | Retrieves cached PnL series |

---

## `OptionsDatabase`

Low-level PostgreSQL connection pool manager executing schema DDL/DML.

```python
from brain_store import OptionsDatabase

db = OptionsDatabase("postgresql://user:pass@localhost:5432/brain")
db.upsert_rl_reward("term_structure", reward=1.45, alpha_id="ALPH_101")
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `upsert_rl_reward` | `(archetype: str, reward: float, alpha_id: str) -> None` | Updates Multi-Armed Bandit state |
| `load_top_performing_exemplars` | `(limit: int = 10) -> list[dict]` | Queries historical best alphas |
| `load_archetype_performance_summary` | `() -> list[dict]` | Aggregates Sharpe & count per archetype |
| `save_correlated_alpha` | `(record: dict) -> None` | Logs candidate rejected by correlation gate |
| `save_rejected_alpha` | `(record: dict) -> None` | Logs candidate failing quality thresholds |
| `close` | `() -> None` | Gracefully closes the connection pool |

---

## `map_archetype_to_core`

Normalizes variant or LLM archetype strings into canonical strategy keys.

```python
from brain_store import map_archetype_to_core

key = map_archetype_to_core("Dynamic Short Squeeze Overhang")
assert key == "dynamic_short_squeeze"
```
