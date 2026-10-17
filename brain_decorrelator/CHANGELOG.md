# Changelog — brain-decorrelator

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-10-17

### Added
- **AST-Diff Engine (`ast_engine`)**:
  - `ASTParser`: Tokenizes and parses WorldQuant Fast Expressions into structured syntax trees (`ASTNode`).
  - `diff.py`: Structural tree difference calculation and motif signature extraction from *AlphaMemo* (Yu et al., 2026).
  - `transformer.py`: Subtree mutation, identifier replacement, and functional wrapping.
- **Asymmetric Veto Memory (`veto_memory`)**:
  - `VetoMemory`: Caches correlation-gate collisions and suppresses repetitive dead-end motifs.
  - `VetoGate`: Pre-filters generated candidates against active veto motifs before platform submission.
- **New Academic Orthogonalization Axes**:
  - `SectorDemeanAxis` (Axis 7): Strips macro sector momentum via cross-sectional residualization.
  - `VolatilityRegimeScalingAxis` (Axis 8): Volatility-scaled signal normalization.
  - `GramSchmidtAxis` (Axis 9): Deflates signals from market beta (SPY proxy).
  - `DecayDilationAxis` (Axis 10): Extends decay lookbacks to 18-30 days, dropping turnover < 4.5% and raising margins > 35 bps.
- **DecorrelationEngine Enhancements**:
  - Added `veto_memory` integration and automatic collision recording on peer failures.

## [0.1.1] — 2026-10-14
- Resolved dependency resolution and PyPI release packaging.

## [0.1.0] — 2026-10-09

### Added
- `AxisPlugin` abstract base class and thread-safe `@register_axis` decorator.
- `unregister_axis()` utility for isolated test environments.
- 6 universal built-in orthogonalization axes:
  - `VelocityDecorrelator` (temporal phase shifting via `ts_delta` and `decay_linear`)
  - `CalendarDecorrelator` (turn-of-month and intra-week seasonal conditioning)
  - `VolumeDecorrelator` (liquidity scaling and volume interaction)
  - `VolatilityDecorrelator` (realized volatility scaling and regime conditioning)
  - `NeutralizationDecorrelator` (cross-sectional group neutralization)
  - `RankDecorrelator` (non-linear power transforms and quantile dispersion)
- Auto-registration of universal axes upon importing `brain_decorrelator`.
- `DecorrelationResult` dataclass with `axis_name`, `transformed_expression`, and `estimated_sharpe_delta`.
- Truncated SHA-256 deduplication for variant suppression.
- PEP 561 compliance marker (`py.typed`).
- Comprehensive unit test suite covering engine, registry, and each orthogonal axis in isolation.
