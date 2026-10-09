# Changelog — brain-options

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-10-09

### Added
- `OptionCandidate` quantitative dataclass inheriting from `brain_core.AlphaCandidate`.
- Complete catalog of 30 options strategies across Volatility Surface, Term Structure, Put-Call Parity, Skew, and Breakeven families.
- Centralized `data/catalog.json` with fallback loader.
- AST-level deduplication delegated to canonical `brain_core.utils.dedup`.
- `passes_quality_gates()` with 4 configurable quantitative gates (G1–G4).
- `OptionsAlphaEngine` orchestrator supporting template rendering and multi-provider LLM generation.
- PEP 561 compliance marker (`py.typed`).
- PyPI packaging configuration with complete metadata.
- Full unit test suite covering archetypes, templates, engine, and catalog loading.
