# Options Expiration Gamma Pinning & Strike Clustering (Strategy 23)

## Academic Foundation
- **Ni, Pearson, Poteshman (2005)**: *Stock Price Clustering on Option Expiration Dates* (Journal of Financial Economics)
- **Garleanu, Pedersen, Poteshman (2009)**: *Demand-Based Option Pricing* (Review of Financial Studies)

## Quantitative Alpha Mechanics
Models dynamic delta-hedging constraints of short gamma dealers ahead of monthly options expirations, capturing structural price pinning around high-open-interest nodes.
- **Turnover Target**: < 15% via `ts_decay_linear(decay=12-18)`.
- **Fitness Invariant**: ≥ 1.00 via volume conviction gating (`volume > adv20 * 0.8`).
