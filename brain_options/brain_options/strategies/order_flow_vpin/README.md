# Institutional Order Flow Toxicity & VPIN (Strategy 22)

## Academic Foundation
- **Easley, Lopez de Prado, O'Hara (2012)**: *Flow Toxicity and Liquidity in a High Frequency World* (Journal of Financial Economics)
- **Lee, Swaminathan (2000)**: *Price Momentum and Trading Volume* (Journal of Finance)

## Quantitative Alpha Mechanics
Captures volume-synchronized order toxicity and informed accumulation by measuring the interaction of volume intensity, price-to-VWAP divergence, and options call flow.
- **Turnover Target**: < 15% via `ts_decay_linear(decay=12-18)`.
- **Fitness Invariant**: ≥ 1.00 via volume conviction gating (`volume > adv20 * 0.8`).
