# Changelog

All notable changes to the `brain-alpha-pipeline` library suite are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), adhering to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-10-09

### Added
- **`brain_core`**: Universal `AlphaCandidate`, `SimSettings`, `SimMetrics` dataclasses; AST deduplication with commutative operator sorting; multi-tier LLM fallback router (Groq, Cerebras, Gemini, OpenRouter).
- **`brain_store`**: Dual-mode relational persistence with `AlphaStore` facade; PostgreSQL connection pooling via `psycopg_pool`; offline JSON/CSV flat-file fallback; schema migration engine.
- **`brain_decorrelator`**: Extensible orthogonal transformation engine with 6 auto-registered axes (Velocity, Neutralization, Volatility, Rank, Volume, Calendar); `@register_axis` plugin interface.
- **`brain_options`**: Implied volatility surface generators; VRP, smirk, term structure, and straddle breakeven mathematical archetypes; literature citations and test suite.
- **`brain_sentiment`**: Standardized Unexpected Earnings (SUE), net revision breadth acceleration, and analyst forecast dispersion arbitrage generators; PEAD decay modeling.
- **`brain_risk_model`**: Betting Against Beta (BAB), idiosyncratic volatility compression, and rolling SPY benchmark correlation divergence archetypes.
- **`brain_synthesis`**: Tri-Factor Apex Meta-Synthesis combining Options (50%), Sentiment (30%), and Systematic Risk (20%); 5 Golden Apex production alphas yielding 1,500+ platform points.
- **Unified CLI**: CLI interface (`python cli.py`) providing `generate`, `decorrelate`, `status`, and `apex` commands.
- **Verification Suite**: Integrated `test_all.py` test runner covering all 86 test cases across the 7 packages.
