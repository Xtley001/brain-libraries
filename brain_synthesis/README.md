# brain-synthesis

Tri-factor apex synthesis engine fusing options, sentiment, and risk-model signals for WorldQuant BRAIN.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-libraries/ci.yml?branch=main)](https://github.com/Xtley001/brain-libraries/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-synthesis)](https://pypi.org/project/brain-synthesis/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_synthesis` combines orthogonal signals across asset classes and information tiers into high-scoring hybrid meta-alphas on WorldQuant BRAIN. By fusing options implied volatility surfaces (50%), analyst earnings revisions (30%), and systematic risk models (20%), it generates super-alphas with sub-0.15 platform correlation and 0.85+ uniqueness. For complete documentation of all 15+ WorldQuant BRAIN dataset field names used in apex formulations, see the [Data Dictionary](./docs/DATA_DICTIONARY.md).

## Installation

```bash
pip install brain-synthesis
```

Installing `brain-synthesis` automatically installs the complete 7-library suite and registers the global `brain` executable.

## Quickstart

### Python API

```python
from brain_synthesis import SynthesisEngine

engine = SynthesisEngine()
golden = engine.get_golden_candidates()

for alpha in golden[:3]:
    print(f"[{alpha.archetype_name}] {alpha.expression}\n")
```

### Unified CLI

```bash
# Generate 3 cross-domain apex meta-alphas
brain generate --domain synthesis --count 3

# Apply 6-axis orthogonal decorrelation
brain decorrelate "rank(close)" --base-sharpe 1.55

# Inspect storage subsystem health
brain store
```

## The 5 Golden Apex Formulations

| Formulation | Leg 1 (Options, 50%) | Leg 2 (Sentiment, 30%) | Leg 3 (Risk Model, 20%) | ValueScore |
|---|---|---|---|:---:|
| **Apex 1: Accumulation Triple** | Put Floor | Analyst Net Revisions | Low SPY Beta | **8.0+** |
| **Apex 2: SUE Smirk Confluence** | Inverted IV Skew | SUE Earnings Shock | Quality / Solvency | **8.0+** |
| **Apex 3: Target Term Slope** | IV Term Structure Slope | Net Target Upgrades | Beta Acceleration | **8.0+** |
| **Apex 4: Torpedo Quality Drift** | Call Breakeven Basis | Revision Divergence | Idiosyncratic Vol | **8.0+** |
| **Apex 5: Attention Asymmetry** | Put Forward Cushion | Coverage Disagreement | Low Market Correlation | **8.0+** |

## Architecture

```
brain_synthesis/
├── brain_synthesis/
│   ├── __init__.py        # Public re-exports (SynthesisEngine, CombinationEngine, ApexCandidate)
│   ├── apex_generator.py  # 5 Golden Apex Formulations
│   ├── cli.py             # Global 'brain' CLI implementation
│   ├── combiner.py        # Dynamic multi-leg weighted synthesizer
│   ├── engine.py          # SynthesisEngine orchestrator
│   └── py.typed           # PEP 561 typing marker
├── tests/                 # Unit tests covering apex generation, combiner, CLI
└── docs/
    ├── API.md             # Complete API specification
    └── DATA_DICTIONARY.md # Comprehensive 15+ WorldQuant BRAIN dataset fields
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
