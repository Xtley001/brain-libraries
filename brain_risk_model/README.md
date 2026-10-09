# brain-risk-model

Systematic factor premia, Betting-Against-Beta, and risk-model alpha generation engine for WorldQuant BRAIN.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-alpha-pipeline/ci.yml?branch=main)](https://github.com/Xtley001/brain-alpha-pipeline/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-risk-model)](https://pypi.org/project/brain-risk-model/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_risk_model` extracts systematic factor premia and risk anomalies from WorldQuant BRAIN risk model datasets (`model51`, `model52`, ValueScore: 7.0). It isolates the low-beta anomaly (Betting-Against-Beta), idiosyncratic volatility compression, and factor rotation into vector-neutral Fast Expressions with sub-industry neutralization. For institutional literature citations and mathematical factor derivations, see the [whitepaper](./docs/whitepaper.md).

## Installation

```bash
pip install brain-risk-model
```

## Quickstart

```python
from brain_risk_model import RiskModelAlphaEngine

engine = RiskModelAlphaEngine()

# Generate 5 systematic risk candidates
candidates = engine.generate_candidates(count=5)

for cand in candidates:
    print(f"[{cand.archetype_name}] Universe: {cand.universe} Decay: {cand.decay}")
    print(f"Formula: {cand.expression}\n")
```

## Systematic Archetypes

| Archetype | Identifier | Core Factor Logic | Economic Hypothesis |
|---|---|---|---|
| **Betting-Against-Beta** | `bab_low_beta` | `ts_decay_linear(rank(-beta_last_60_days_spy), d)` | Leverage-constrained investors overbid high-beta assets, making low-beta assets structurally underpriced. |
| **Idiosyncratic Volatility** | `idio_vol_discount` | `ts_decay_linear(rank(-idio_vol_last_60_days), d)` | Stocks with high idiosyncratic volatility suffer from retail lottery demand and underperform over intermediate horizons. |
| **Residual Momentum** | `residual_mom_spread` | `rank(ts_decay_linear(mom - beta * spy_return, d))` | Momentum calculated after stripping systematic market and sector beta generates superior risk-adjusted Sharpe. |
| **Value-Growth Dispersion** | `val_growth_divergence` | `rank(value_score) - rank(growth_score)` | Macro valuation dislocations between cash-flow multiples and speculative growth expectations revert cyclically. |
| **Quality / Leverage Spread** | `quality_solvency_spread` | `rank(fscore_bfl_quality) - rank(leverage_last_quarter)` | Isolates firms compounding returns with self-funded cash flow over debt-financed expansion. |
| **Low-Risk Regime Gate** | `low_vol_regime` | `trade_when(volatility_120 < ts_mean(...), rank(bab), -1)` | Activates factor exposure conditionally during calm volatility regimes when factor premia are most reliable. |

## Architecture

```
brain_risk_model/
├── brain_risk_model/
│   ├── __init__.py        # Public re-exports (RiskModelAlphaEngine, RiskModelCandidate)
│   ├── data/
│   │   └── catalog.json   # Live BRAIN risk model field catalog
│   ├── catalog.py         # RiskModelCatalog loader & field groupings
│   ├── archetypes.py      # Systematic factor archetype descriptors
│   ├── dedup.py           # AST expression deduplicator (delegates to brain_core)
│   ├── generator.py       # Candidate generation engine
│   ├── py.typed           # PEP 561 typing marker
│   └── strategies/        # Modular strategy implementations for all 6 archetypes
├── tests/                 # Unit tests covering catalog, engine, strategies, templates
└── docs/
    ├── API.md             # Complete API specification
    └── whitepaper.md      # Systematic risk model premia & BAB theory
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
