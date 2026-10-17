# brain-synthesis

Tri-factor apex synthesis engine with Hierarchical Risk Parity (HRP) and dynamic regime adaptation for WorldQuant BRAIN.

[![CI](https://img.shields.io/github/actions/workflow/status/Xtley001/brain-libraries/ci.yml?branch=main)](https://github.com/Xtley001/brain-libraries/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brain-synthesis)](https://pypi.org/project/brain-synthesis/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Total Downloads](https://img.shields.io/pepy/dt/brain-synthesis?label=downloads)](https://pepy.tech/projects/brain-synthesis)

`brain_synthesis` combines orthogonal signals across asset classes and information tiers into high-scoring hybrid meta-alphas on WorldQuant BRAIN. By fusing options implied volatility surfaces, analyst earnings revisions, and systematic risk premia using **Hierarchical Risk Parity (HRP)** and **Dynamic Regime Detection**, it generates super-alphas yielding 1,600+ platform points with sub-0.50 platform correlation and 0.85+ uniqueness.

## Installation

```bash
pip install brain-synthesis
```

Installing `brain-synthesis` automatically installs the complete 7-library suite and registers the global `brain` executable.

## Quickstart

### 1. The 8 Golden Apex Formulations
```python
from brain_synthesis import generate_apex_candidates

# Generate golden apex candidates across TOP3000, TOP2000, TOP1000
candidates = generate_apex_candidates(universes=["TOP3000", "TOP1000"], decays=[15, 20])

for alpha in candidates[:3]:
    print(f"[{alpha.archetype_name}] {alpha.expression}\n")
```

### 2. Hierarchical Risk Parity (HRP) Synthesis
```python
from brain_core.types import AlphaCandidate
from brain_synthesis import DynamicSynthesizer

syn = DynamicSynthesizer()

leg_options = AlphaCandidate(expression="rank(implied_volatility_call_30)", archetype_name="opt")
leg_sentiment = AlphaCandidate(expression="rank(snt1_d1_netearningsrevision)", archetype_name="snt")
leg_risk = AlphaCandidate(expression="rank(beta_last_60_days_spy)", archetype_name="risk")

# Empirical covariance matrix between legs
cov_matrix = [
    [0.04, 0.005, 0.002],
    [0.005, 0.02, 0.001],
    [0.002, 0.001, 0.01],
]

# Computes tree clustering & recursive bisection without matrix inversion
apex = syn.synthesize_hrp(
    candidates=[leg_options, leg_sentiment, leg_risk],
    cov_matrix=cov_matrix,
    name="My_HRP_Super_Alpha",
    universe="TOP3000",
)
print("Synthesized HRP Expression:", apex.expression)
```

### 3. Dynamic Market Regime Synthesis
```python
from brain_synthesis import DynamicSynthesizer, MarketRegime

syn = DynamicSynthesizer()

# In high-volatility regimes, automatically boosts options skew and tail protection
apex_vol = syn.synthesize_regime(
    candidates=[leg_options, leg_sentiment, leg_risk],
    regime=MarketRegime.HIGH_VOLATILITY,
    universe="TOP1000",
)
print("High-Vol Adaptive Expression:", apex_vol.expression)
```

### 4. Unified CLI
```bash
# Generate 3 cross-domain apex meta-alphas
brain generate --domain synthesis --count 3

# Apply 10-axis orthogonal decorrelation
brain decorrelate "rank(close)" --base-sharpe 1.55

# Inspect storage subsystem health
brain store
```

## The 8 Golden Tri-Factor Formulations

| Formulation | Leg 1 (Options) | Leg 2 (Sentiment) | Leg 3 (Risk / Fundamental) | ValueScore |
|---|---|---|---|:---:|
| **Apex 1: Accumulation Triple** | Put Support Floor | Analyst Net Revisions | Low SPY Beta (BAB) | **8.5+** |
| **Apex 2: SUE Smirk Confluence** | Inverted IV Skew Smirk | SUE Earnings Shock | Quality / Solvency Accel | **8.5+** |
| **Apex 3: Target Term Slope** | 180d vs 30d IV Term Slope | Net Target Upgrades | Beta Demean | **8.5+** |
| **Apex 4: Torpedo Quality Drift** | Call Breakeven Basis | Disappointment Re-rating | Accounting F-Score Quality | **8.5+** |
| **Apex 5: Attention Asymmetry** | Put Forward Cushion | Analyst Search Attention | Low SPY Correlation | **8.5+** |
| **Apex 6: Toxic Flow Squeeze** *(New)* | VPIN Volume Imbalance | Consensus Dispersion | Borrow Utilization Surge | **9.0+** |
| **Apex 7: Gross Profitability Basis** *(New)*| Synthetic Forward Basis | Revenue Revision Drift | Novy-Marx Gross Profitability| **9.0+** |
| **Apex 8: Borrow Friction Drift** *(New)* | Put/Call OI Positioning | Institutional Ownership Delta | Loan Fee Momentum | **9.0+** |

## Architecture

```
brain_synthesis/
├── hrp/                         # Hierarchical Risk Parity (López de Prado, AFML)
│   ├── clustering.py            # Correlation metric distance & tree clustering
│   └── bisection.py             # Recursive bisection weight allocation
├── regime_engine/               # Dynamic regime adaptation (AQuA, 2026)
│   ├── detector.py              # Macro regime detector (Vol, Earnings, Trending, Neutral)
│   └── dynamic_weights.py       # Regime-conditional factor weight tuner
├── apex_generator.py            # 8 Golden Tri-Factor Apex Archetypes across 6 universes
├── combiner.py                  # DynamicSynthesizer supporting manual, HRP, and regime weighting
├── engine.py                    # Master SynthesisEngine multi-generator orchestrator
├── cli.py                       # Unified 'brain' command-line interface
└── py.typed                     # PEP 561 compliance marker
```

## Testing

```bash
pytest tests/ -v
```

## License

Released under the [MIT License](../LICENSE). Maintained by [Xtley001](https://github.com/Xtley001).
