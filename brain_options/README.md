# brain-options

Options-trading alpha generation engine (implied vol, skew, term structure, breakeven) for WorldQuant BRAIN.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-alpha-pipeline/ci.yml?branch=main)](https://github.com/Xtley001/brain-alpha-pipeline/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-options)](https://pypi.org/project/brain-options/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_options` generates institutional quantitative alphas on WorldQuant BRAIN options datasets (`option8`, `option9`, ValueScore: 6.0). It codifies 30 mathematical archetypes across implied volatility surfaces, skew, term structure, and straddle breakevens into vector-neutral Fast Expressions with automated AST deduplication. For institutional literature citations and surface derivations, see the [whitepaper](./docs/whitepaper.md).

## Installation

```bash
pip install brain-options
```

## Quickstart

```python
from brain_options import OptionsAlphaEngine

engine = OptionsAlphaEngine()

# Generate 5 vector-neutral options alpha candidates
candidates = engine.generate_candidates(count=5)

for cand in candidates:
    print(f"[{cand.tags}] {cand.expression}\n")
```

## Core Options Archetypes

| Archetype | Institutional Literature | Formula Concept | ValueScore |
|---|---|---|:---:|
| **Volatility Smirk** | Xing, Zhang & Zhao (2010) | OTM Put IV minus ATM Call IV captures informed downside hedging | **6.0** |
| **Term Structure Slope** | An, Ang, Bali & Cakici (2014) | Slope between 30d and 90d implied volatility tracks event risk pricing | **6.0** |
| **Variance Risk Premium** | Sinclair (2010), Bali (2008) | Implied volatility minus realized historical volatility (IV - RV) | **6.0** |
| **Breakeven Drift** | Sinclair (2010) | Forward price divergence from straddle put breakeven levels | **6.0** |

## Architecture

```
brain_options/
├── brain_options/
│   ├── __init__.py        # Public re-exports (OptionsAlphaEngine, OptionCandidate)
│   ├── data/
│   │   └── catalog.json   # Live BRAIN options field catalog
│   ├── catalog.py         # OptionsCatalog field groupings & loader
│   ├── archetypes.py      # Quantitative options strategy descriptors
│   ├── dedup.py           # AST expression deduplicator (delegates to brain_core)
│   ├── generator.py       # Candidate generation engine
│   ├── py.typed           # PEP 561 typing marker
│   └── strategies/        # Modular strategy families (skew, surface, term_structure)
├── tests/                 # Unit tests covering catalog, engine, filter, candidate
└── docs/
    ├── API.md             # Complete API specification
    └── whitepaper.md      # Quantitative options theory & surface formulations
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
