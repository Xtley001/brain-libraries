# brain-decorrelator API Reference

Strategy-agnostic orthogonal decorrelation plugin engine. Converts correlated signals into independent variants.

## `DecorrelationEngine`

Main stateless transformation engine.

```python
from brain_decorrelator import DecorrelationEngine

engine = DecorrelationEngine()
results = engine.generate_orthogonal_variants(
    base_expr="rank(ts_decay_linear(close, 10))",
    archetype="momentum",
    base_sharpe=1.55,
)

for r in results:
    print(f"[{r.axis_name}] {r.expression}")
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `generate_orthogonal_variants` | `(base_expr: str, archetype: str, base_sharpe: float = 1.5, colliding_id: str \| None = None, colliding_factor: str \| None = None, context: dict \| None = None) -> list[DecorrelationResult]` | Applies all registered transforms and returns SHA-256 deduplicated variants |

---

## `DecorrelationResult`

Named tuple holding a synthesized variant and associated metadata.

| Field | Type | Description |
|---|---|---|
| `expression` | `str` | Orthogonalized Fast Expression string |
| `axis_name` | `str` | Name of the transform axis applied |
| `archetype_name` | `str` | Strategy archetype identifier |
| `hypothesis` | `str` | Generated economic hypothesis |
| `base_alpha_id` | `str \| None` | Source alpha ID if derived from existing candidate |

---

## `AxisPlugin` & `@register_axis`

Abstract Base Class and decorator for custom domain orthogonalization plugins.

```python
from brain_decorrelator import AxisPlugin, register_axis

@register_axis
class CustomShiftAxis(AxisPlugin):
    name = "Custom Shift Axis"

    def apply(self, expr: str, context: dict) -> list[str]:
        if "rank(" in expr:
            return [expr.replace("rank(", "group_rank(")]
        return []
```

### Universal Axes Included

1. `VelocityShiftAxis`: Wraps inner decay variables in `ts_delta` rate-of-change.
2. `CalendarSpreadAxis`: Replaces single-tenor fields with cross-tenor spreads.
3. `VolumeRegimeAxis`: Gates signal on `volume > adv20 * multiplier`.
4. `VolatilityRegimeAxis`: Gates signal on volatility expansion regime.
5. `NeutralizationRotationAxis`: Swaps `subindustry` $\leftrightarrow$ `sector`.
6. `CrossSectionalRankAxis`: Normalizes un-ranked root signals with `group_rank`.
