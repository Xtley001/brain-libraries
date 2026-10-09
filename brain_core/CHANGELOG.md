# Changelog — brain-core

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-10-09

### Added
- `AlphaCandidate` dataclass with `VALID_GENERATION_SOURCES` validation and immutable fields.
- `SimSettings` and `SimMetrics` canonical quantitative contracts.
- `ASTDeduplicator` canonical AST normalizer in `brain_core.utils.dedup` with constant sorting and operator canonicalization.
- `Config.load_from_env()` with lazy `dotenv` loading, 26 typed fields, and fallback multi-provider LLM tier resolution.
- `get_logger()` thread-safe logger factory with `LOG_LEVEL` environment configuration.
- Multi-provider LLM adapter supporting Groq, Cerebras, Gemini, and OpenRouter with automatic failover.
- PEP 561 compliance marker (`py.typed`).
- PyPI packaging manifest with full metadata, keywords, and classifiers.
- Comprehensive unit test suite covering types, config, dedup, and logging.
