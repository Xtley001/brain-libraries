# Changelog — brain-synthesis

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-10-17

### Added
- **Hierarchical Risk Parity (HRP) Module (`hrp`)**:
  - `compute_correlation_distance_matrix`: Proper metric space correlation distance $D_{i,j} = \sqrt{0.5 \times (1 - \rho_{i,j})}$.
  - `hierarchical_cluster_indices`: Single-linkage hierarchical agglomerative tree clustering.
  - `recursive_bisection`: Calculates risk-parity cluster weights without matrix inversion (López de Prado, AFML Chapter 16).
- **Dynamic Regime Engine (`regime_engine`)**:
  - `MarketRegimeDetector`: Automatically detects `HIGH_VOLATILITY`, `EARNINGS_SEASON`, `TRENDING`, and `NEUTRAL` macro regimes.
  - `RegimeAwareWeightTuner`: Dynamically tunes alpha leg weights based on regime confidence (AQuA, Guo et al., 2026).
- **8 Golden Tri-Factor Apex Archetypes (`apex_generator`)**:
  - Expanded from 5 to 8 institutional formulations covering all 6 platform universes (`TOP3000`, `TOP2000`, `TOP1000`, `TOP500`, `TOP200`, `TOPSP500`).
  - Added `Apex6_Toxic_Flow_Squeeze`: Directional volume imbalance (VPIN) × analyst dispersion × borrow fee surge.
  - Added `Apex7_Gross_Profitability_Basis`: Synthetic forward basis parity × revenue revisions × Novy-Marx gross profitability.
  - Added `Apex8_Borrow_Friction_Drift`: Put/call open interest positioning × institutional accumulation × loan fee momentum.
- **DynamicSynthesizer Upgrades (`combiner`)**:
  - Added `synthesize_hrp(...)` for automated HRP weighting.
  - Added `synthesize_regime(...)` for regime-adaptive synthesis.

## [0.1.1] — 2026-10-14
- Resolved cross-package dependency resolution and PyPI release packaging.

## [0.1.0] — 2026-10-09

### Added
- `SynthesisEngine` cross-category orchestrator generating tri-factor apex meta-alphas.
- `CombinationEngine` multi-factor combiner supporting dynamic weighting and non-linear interactions.
- `ApexCandidate` quantitative model subclassing `brain_core.AlphaCandidate`.
- 5 Apex hybrid formulations synthesizing Options, Sentiment, and Systematic Risk factors.
- Global `brain` Command Line Interface (`cli.py`) entry point registered in `[project.scripts]`.
- Cross-domain fault isolation: synthesis proceeds gracefully even if individual domain generators fail.
- `DATA_DICTIONARY.md` documenting all 15+ WorldQuant BRAIN dataset field names.
- PEP 561 compliance marker (`py.typed`).
- PyPI packaging configuration with complete metadata.
- Comprehensive unit tests covering combination logic, apex candidate generation, and CLI commands.
