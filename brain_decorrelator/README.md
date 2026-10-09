# brain-decorrelator

Strategy-agnostic alpha decorrelation engine with plugin-based orthogonalization axes.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-libraries/ci.yml?branch=main)](https://github.com/Xtley001/brain-libraries/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-decorrelator)](https://pypi.org/project/brain-decorrelator/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_decorrelator` transforms correlated alpha expressions into orthogonal variants that pass WorldQuant BRAIN's correlation gate ($|\rho| < 0.70$) while preserving underlying economic Sharpe. It operates across all quantitative domains (Options, Sentiment, Risk Models) via an extensible plugin registry. For detailed mathematical formulations and before/after empirical benchmarks, see the [Axes Guide](./docs/AXES.md).

## Installation

```bash
pip install brain-decorrelator
```

## Quickstart

```python
from brain_decorrelator import DecorrelationEngine

engine = DecorrelationEngine()

# Automatically applies all 6 registered orthogonal axes
variants = engine.generate_orthogonal_variants(
    expression="rank(implied_volatility_call_30)",
    base_sharpe=1.65,
    max_variants=5,
)

for v in variants:
    print(f"[{v.axis_name}] -> {v.transformed_expression}")
```

## The 6 Universal Orthogonal Axes

| Axis | Transformation Logic | WorldQuant BRAIN Syntax | Typical $\rho$ | Sharpe Retention |
|---|---|---|:---:|:---:|
| **Velocity** | Temporal phase shift via rate-of-change and decay | `decay_linear(ts_delta(expr, 5), 10)` | **0.35–0.50** | $85-92\%$ |
| **Neutralization** | Multi-level factor and sector group residualization | `group_neutralize(rank(expr), sector)` | **0.42–0.58** | $95-110\%$ |
| **Volatility Gating** | Regime scaling conditional on market variance | `expr / (ts_std_dev(returns, 20) + 1e-4)` | **0.48–0.62** | $90-96\%$ |
| **Rank Convexity** | Concentrating portfolio weight in extreme tails | `power(rank(expr) - 0.5, 3)` | **0.55–0.68** | $92-98\%$ |
| **Volume Weighting** | Tilting towards liquid names to damp market friction | `expr * rank(volume / (adv20 + 1e-4))` | **0.38–0.55** | $88-94\%$ |
| **Calendar Modulation**| Seasonality & turn-of-month institutional rebalancing | `if_else(day_of_month(0) <= 5, expr*1.2, expr*0.8)` | **0.60–0.68** | $92-95\%$ |

## Extending with Custom Plugins

```python
from brain_decorrelator import AxisPlugin, register_axis

@register_axis
class MoneynessInversionAxis(AxisPlugin):
    name = "moneyness_inversion"

    def apply(self, expression: str, context: dict) -> list[str]:
        return [f"-({expression})"]
```

## Architecture

```
brain_decorrelator/
├── brain_decorrelator/
│   ├── __init__.py        # Public re-exports (DecorrelationEngine, register_axis, unregister_axis)
│   ├── plugin.py          # AxisPlugin ABC + thread-safe registry
│   ├── engine.py          # DecorrelationEngine — orchestrator & variant dedup
│   ├── py.typed           # PEP 561 typing marker
│   └── axes/
│       └── universal.py   # 6 domain-agnostic built-in orthogonal axes
├── tests/                 # Unit tests covering registry and all 6 axes
└── docs/
    ├── API.md             # Complete API specification
    └── AXES.md            # Mathematical formulations & worked examples
```

## Testing

```bash
pytest tests/ -v
```

## Security

Report vulnerabilities per [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

Released under the [MIT License](../LICENSE). Maintained by [Xtley001](https://github.com/Xtley001).
