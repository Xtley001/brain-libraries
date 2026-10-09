# brain-sentiment

Analyst revisions, PEAD, and sentiment alpha generation engine for WorldQuant BRAIN.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-alpha-pipeline/ci.yml?branch=main)](https://github.com/Xtley001/brain-alpha-pipeline/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-sentiment)](https://pypi.org/project/brain-sentiment/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_sentiment` generates quantitative equity alphas on WorldQuant BRAIN sentiment and revision datasets (`sentiment1`, `sentiment2`, ValueScore: 8.0). It codifies Post-Earnings Announcement Drift (PEAD), Standardized Unexpected Earnings (SUE), and analyst revision diffusion into turnover-controlled (< 12%) Fast Expressions with sub-industry neutralization. For institutional literature citations and mathematical derivations, see the [whitepaper](./docs/whitepaper.md).

## Installation

```bash
pip install brain-sentiment
```

## Quickstart

```python
from brain_sentiment import SentimentAlphaEngine

engine = SentimentAlphaEngine()

# Generate 5 turnover-controlled sentiment candidates
candidates = engine.generate_candidates(count=5)

for cand in candidates:
    print(f"[{cand.tags}] {cand.expression}\n")
```

## Core Sentiment Archetypes

| Archetype | Institutional Literature | Economic Hypothesis | ValueScore |
|---|---|---|:---:|
| **SUE Drift** | Bernard & Thomas (1989) | Standardized quarterly earnings surprises drift predictably for 60-90 days | **8.0** |
| **Revision Breadth** | Chan et al. (1996) | Net fraction of upward vs downward analyst revisions leads momentum | **8.0** |
| **Dispersion Arbitrage**| Diether et al. (2002) | Equities with high sell-side forecast disagreement suffer optimistic overpricing | **8.0** |
| **Revision Divergence** | Livnat & Mendenhall (2006) | Accelerating upward revisions lagging equity price provide reliable forward drift | **8.0** |

## Architecture

```
brain_sentiment/
├── brain_sentiment/
│   ├── __init__.py        # Public re-exports (SentimentAlphaEngine, SentimentCandidate)
│   ├── data/
│   │   └── catalog.json   # Live BRAIN sentiment field catalog
│   ├── catalog.py         # SentimentCatalog field groupings & loader
│   ├── archetypes.py      # Quantitative sentiment strategy descriptors
│   ├── dedup.py           # AST expression deduplicator (delegates to brain_core)
│   ├── generator.py       # Candidate generation engine
│   ├── py.typed           # PEP 561 typing marker
│   └── strategies/        # Modular strategy implementations (pead, revision_breadth)
├── tests/                 # Unit tests covering catalog, engine, strategies, templates
└── docs/
    ├── API.md             # Complete API specification
    └── whitepaper.md      # Quantitative sentiment theory & PEAD dynamics
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
