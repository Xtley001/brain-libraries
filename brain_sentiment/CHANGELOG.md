# Changelog — brain-sentiment

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-10-09

### Added
- `SentimentCandidate` quantitative dataclass extending `brain_core.AlphaCandidate`.
- Catalog of PEAD, Standardized Unexpected Earnings (SUE), analyst revision diffusion, and news attention strategy families.
- Centralized `data/catalog.json` with fallback loader.
- AST-level deduplication delegated to canonical `brain_core.utils.dedup`.
- `SentimentAlphaEngine` generation pipeline supporting template rendering and LLM prompt generation.
- Specialists knowledge base (`kb.py`) encoding Chan, Bernard & Thomas, and Diether institutional heuristics.
- PEP 561 compliance marker (`py.typed`).
- PyPI packaging configuration with complete metadata.
- Full unit test suite covering archetypes, templates, engine, and catalog loading.
