# brain-risk-model API Reference

Systematic factor premia, low-volatility anomaly, and Betting-Against-Beta alpha pipeline.

## `RiskModelAlphaEngine`

Orchestrates systematic risk model alpha generation.

```python
from brain_risk_model import RiskModelAlphaEngine

engine = RiskModelAlphaEngine()
cands = engine.generate_candidates(count=5)
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `generate_candidates` | `(count: int = 10) -> list[RiskModelCandidate]` | Generates risk model candidates |
| `decorrelate_candidate` | `(candidate: RiskModelCandidate, base_sharpe: float = 1.30) -> list[DecorrelationResult]` | Generates orthogonalized variants |

---

## `RiskModelCandidate`

Dataclass for systematic factor alpha candidates.

| Field | Type | Default | Description |
|---|---|---|---|
| `expression` | `str` | *(required)* | Fast Expression string |
| `archetype` | `str` | *(required)* | Strategy archetype |
| `family` | `str` | *(required)* | Strategy family |
| `hypothesis` | `str` | *(required)* | Economic hypothesis |
| `universe` | `str` | `"TOP3000"` | Investment universe |
| `neutralization` | `str` | `"SUBINDUSTRY"` | Neutralization group |
| `decay` | `int` | `15` | Signal decay smoothing |
