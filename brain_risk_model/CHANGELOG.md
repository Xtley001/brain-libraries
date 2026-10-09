# Changelog — brain-risk-model

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-10-09

### Added
- `RiskModelCandidate` quantitative dataclass extending `brain_core.AlphaCandidate`.
- Systematic factor archetypes covering Betting-Against-Beta (BAB), Idiosyncratic Volatility, Quality, Leverage, and Low-Vol premia.
- Centralized `data/catalog.json` with fallback loader.
- AST-level deduplication delegated to canonical `brain_core.utils.dedup`.
- `RiskModelAlphaEngine` generation pipeline supporting template rendering and prompt generation.
- Institutional factor formulas derived from Frazzini & Pedersen (2014) and Ang et al. (2006).
- PEP 561 compliance marker (`py.typed`).
- PyPI packaging configuration with complete metadata.
- Full unit test suite covering archetypes, templates, engine, and catalog loading.
