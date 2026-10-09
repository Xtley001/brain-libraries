# brain-core

Core utilities, configuration, AST deduplication, and shared data models for the Brain Alpha Engine.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-alpha-pipeline/ci.yml?branch=main)](https://github.com/Xtley001/brain-alpha-pipeline/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-core)](https://pypi.org/project/brain-core/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`brain_core` is the foundational contract and utility layer for the 7-library Brain Alpha suite. It defines the canonical `AlphaCandidate` dataclass, manages environment configuration with deferred `.env` loading, provides AST-level expression deduplication, and coordinates multi-provider LLM failover. For the formal type contract and normalization invariants, see the [whitepaper](./docs/whitepaper.md).

## Installation

```bash
pip install brain-core
```

## Quickstart

```python
from brain_core import Config, get_logger, SimSettings, SimMetrics, AlphaCandidate
from brain_core.utils.dedup import ASTDeduplicator

cfg = Config.load_from_env()
log = get_logger(__name__)

# Normalize and deduplicate expressions canonically
dedup = ASTDeduplicator()
norm_expr = dedup.normalize_expression("close + open")

settings = SimSettings(universe="TOP3000", delay=1, decay=15)
candidate = AlphaCandidate(
    alpha_id="alpha_001",
    expression=norm_expr,
    category="option",
    generation_source="template",
    settings=settings,
)
```

## Architecture

```
brain_core/
├── brain_core/
│   ├── __init__.py        # Public re-exports
│   ├── config.py          # Config dataclass + lazy env loader
│   ├── logger.py          # get_logger() factory
│   ├── llm.py             # Multi-provider LLM tier adapter
│   ├── py.typed           # PEP 561 typing marker
│   ├── types.py           # SimSettings, SimMetrics, AlphaCandidate
│   └── utils/
│       ├── __init__.py
│       └── dedup.py       # ASTDeduplicator canonical normalizer
├── tests/                 # Pytest test suite
└── docs/
    ├── API.md             # Complete API specification
    └── whitepaper.md      # Quantitative type contract & AST specification
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
