# Dynamic Short Squeeze & Borrow Fee Convexity (Strategy 21)

## Academic Foundation
- **Engelberg, Reed, Ringgenberg (2018)**: *Short-Selling Risk* (Journal of Finance)
- **Kolasinski, Reed, Ringgenberg (2013)**: *A Multiple Lender Approach to Understanding Supply and Search in the Equity Lending Market*

## Quantitative Alpha Mechanics
Captures non-linear short recall pressure by tracking the acceleration in annualized equity borrow fees combined with short interest float.
- **Turnover Target**: < 15% via `ts_decay_linear(decay=12-18)`.
- **Fitness Invariant**: ≥ 1.00 via volume conviction gating (`volume > adv20 * 0.8`).
