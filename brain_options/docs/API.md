# brain-options API Reference

Options derivatives alpha generation, AST invariant enforcement, and quality screening pipeline.

## `OptionsAlphaEngine`

Top-level facade coordinating generation, screening, and orthogonalization.

```python
from brain_options import OptionsAlphaEngine

engine = OptionsAlphaEngine()
candidates = engine.generate_candidates(count=5)
variants = engine.decorrelate_candidate(candidates[0], base_sharpe=1.45)
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `generate_candidates` | `(count: int = 10) -> list[OptionCandidate]` | Pulls high-conviction candidate expressions |
| `decorrelate_candidate` | `(candidate: OptionCandidate, base_sharpe: float = 1.30) -> list[DecorrelationResult]` | Generates orthogonalized variants |
| `evaluate_gates` | `(metrics: SimMetrics) -> tuple[bool, str]` | Evaluates G1-G4 Sharpe/Fitness/Turnover gates |

---

## `OptionCandidate`

Dataclass extending `AlphaCandidate` with options domain fields.

| Field | Type | Default | Description |
|---|---|---|---|
| `expression` | `str` | *(required)* | Fast Expression string |
| `archetype_name` | `str` | *(required)* | Archetype label |
| `hypothesis` | `str` | `""` | Economic rationale |
| `universe` | `str` | `"TOP3000"` | Investment universe |
| `neutralization` | `str` | `"SUBINDUSTRY"` | Neutralization group |
| `delay` | `int` | `1` | Simulation delay |
| `decay` | `int` | `8` | Signal decay smoothing |

---

## `OptionsCatalog`

Live BRAIN options dataset catalog containing all 138 options fields.

```python
from brain_options import OptionsCatalog

catalog = OptionsCatalog()
field = catalog.get_field("forward_price_30")
subfams = catalog.subfamilies()
```

---

## `compile_fitness_invariant`

Parses expressions into ASTs and injects subindustry neutralization, liquidity armor, and smoothing.

```python
from brain_options import compile_fitness_invariant

clean_expr = compile_fitness_invariant("forward_price_30 - put_breakeven_30")
```
