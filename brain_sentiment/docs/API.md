# brain-sentiment API Reference

Analyst expectations, post-earnings announcement drift (PEAD), and news sentiment pipeline.

## `SentimentAlphaEngine`

Orchestrates sentiment candidate generation and decorrelation.

```python
from brain_sentiment import SentimentAlphaEngine

engine = SentimentAlphaEngine()
cands = engine.generate_candidates(count=5)
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `generate_candidates` | `(count: int = 10) -> list[SentimentCandidate]` | Generates sentiment alpha candidates |
| `decorrelate_candidate` | `(candidate: SentimentCandidate, base_sharpe: float = 1.30) -> list[DecorrelationResult]` | Generates orthogonalized variants |

---

## `SentimentCandidate`

Dataclass for sentiment alpha candidates.

| Field | Type | Default | Description |
|---|---|---|---|
| `expression` | `str` | *(required)* | Fast Expression string |
| `archetype` | `str` | *(required)* | Strategy archetype |
| `family` | `str` | *(required)* | Strategy family |
| `hypothesis` | `str` | *(required)* | Economic hypothesis |
| `universe` | `str` | `"TOP3000"` | Investment universe |
| `neutralization` | `str` | `"SUBINDUSTRY"` | Neutralization group |
| `decay` | `int` | `15` | Signal decay smoothing |

---

## `compile_sentiment_invariant`

Enforces turnover < 15%, liquidity armor, and subindustry neutralization invariants on sentiment signals.

```python
from brain_sentiment import compile_sentiment_invariant

expr = compile_sentiment_invariant("snt1_d1_netearningsrevision", default_decay=15)
```
