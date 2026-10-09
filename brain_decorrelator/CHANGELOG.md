# Changelog — brain-decorrelator

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
