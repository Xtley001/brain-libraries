# brain-synthesis API Reference

Tri-factor cross-asset alpha synthesis engine fusing options, sentiment, and risk models.

## `SynthesisEngine`

Top-level orchestrator for golden formulations and multi-leg dynamic synthesis.

```python
from brain_synthesis import SynthesisEngine

engine = SynthesisEngine()
golden_cands = engine.get_golden_candidates()
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `get_golden_candidates` | `() -> list[ApexCandidate]` | Returns the 5 Golden Apex Formulations |
| `synthesize_cross_domain` | `(legs: list[tuple[AlphaCandidate, float]], name: str = "CrossDomain_Synthesis") -> ApexCandidate` | Fuses arbitrary signals into ranked composite |
| `decorrelate_candidate` | `(candidate: ApexCandidate, base_sharpe: float = 1.40) -> list[DecorrelationResult]` | Decorrelates synthesized alpha |

---

## `DynamicSynthesizer`

Combines arbitrary weighted signals across domains.

```python
from brain_synthesis import DynamicSynthesizer
from brain_core.types import AlphaCandidate

synthesizer = DynamicSynthesizer()
leg1 = AlphaCandidate(expression="rank(close)", archetype_name="opt")
leg2 = AlphaCandidate(expression="snt1_d1_netearningsrevision", archetype_name="snt")

composite = synthesizer.synthesize([(leg1, 0.60), (leg2, 0.40)], name="Apex_Custom")
```

---

## `ApexCandidate`

Dataclass for synthesized meta-alphas.

| Field | Type | Default | Description |
|---|---|---|---|
| `expression` | `str` | *(required)* | Fused Fast Expression string |
| `archetype_name` | `str` | *(required)* | Archetype label |
| `name` | `str` | `""` | Synthesis formulation name |
| `universe` | `str` | `"TOP3000"` | Investment universe |
| `neutralization` | `str` | `"SUBINDUSTRY"` | Neutralization group |
| `decay` | `int` | `15` | Signal decay smoothing |
| `category` | `str` | `"hybrid_tri_factor"` | BRAIN category |
