# Changelog — brain-synthesis

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
