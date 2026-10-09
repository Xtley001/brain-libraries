# brain-core API Reference

## `Config`

```python
from brain_core import Config
cfg = Config.load_from_env()
```

All fields are immutable (frozen dataclass).

| Field | Type | Default | Env var |
|---|---|---|---|
| `brain_username` | `str` | `""` | `BRAIN_USERNAME` |
| `brain_password` | `str` | `""` | `BRAIN_PASSWORD` |
| `brain_max_concurrent_sims` | `int` | `3` | `BRAIN_MAX_CONCURRENT_SIMS` |
| `groq_keys` | `list[str]` | `[]` | `GROQ_API_KEY[_1..9]` |
| `cerebras_keys` | `list[str]` | `[]` | `CEREBRAS_API_KEY[_1..9]` |
| `openrouter_keys` | `list[str]` | `[]` | `OPENROUTER_API_KEY[_1..9]` |
| `gemini_keys` | `list[str]` | `[]` | `GEMINI_API_KEY[_1..9]` |
| `telegram_bot_token` | `str \| None` | `None` | `TELEGRAM_BOT_TOKEN` |
| `telegram_chat_id` | `str \| None` | `None` | `TELEGRAM_CHAT_ID` |
| `database_url` | `str \| None` | `None` | `DATABASE_URL` |
| `stage0_min_sharpe` | `float` | `0.60` | `STAGE0_MIN_SHARPE` |
| `stage0_min_fitness` | `float` | `0.50` | `STAGE0_MIN_FITNESS` |
| `filter_min_sharpe` | `float` | `1.25` | `FILTER_MIN_SHARPE` |
| `filter_min_fitness` | `float` | `1.00` | `FILTER_MIN_FITNESS` |
| `filter_min_turnover` | `float` | `0.01` | `FILTER_MIN_TURNOVER` |
| `filter_max_turnover` | `float` | `0.70` | `FILTER_MAX_TURNOVER` |
| `max_pool_correlation` | `float` | `0.70` | `MAX_POOL_CORRELATION` |
| `universe` | `str` | `"TOP3000"` | `UNIVERSE` |
| `delay` | `int` | `1` | `DELAY` |
| `max_candidates_per_run` | `int` | `10` | `MAX_CANDIDATES_PER_RUN` |
| `run_time_budget_seconds` | `int` | `480` | `RUN_TIME_BUDGET_SECONDS` |
| `drip_max_daily` | `int` | `1` | `DRIP_MAX_DAILY` |
| `drip_min_interval_hours` | `float` | `4.0` | `DRIP_MIN_INTERVAL_HOURS` |
| `enable_auto_submit` | `bool` | `False` | `ENABLE_AUTO_SUBMIT` |

## `get_logger`

```python
from brain_core import get_logger
log = get_logger(__name__)
log.info("Pipeline started")
```

## `SimSettings`

```python
from brain_core import SimSettings
s = SimSettings(universe="TOP2000", decay=12)
payload = s.to_simulation_payload("rank(close)")
```

## `SimMetrics`

```python
from brain_core import SimMetrics
m = SimMetrics(status="COMPLETE", sharpe=1.5, fitness=1.1)
assert m.is_valid
assert m.passed_stage0()
```

## `AlphaCandidate`

```python
from brain_core import AlphaCandidate
cand = AlphaCandidate(
    expression="rank(close)",
    archetype_name="Momentum",
    hypothesis="Price persistence signal.",
)
```
