# Customer-Supplier Revenue Concentration & Cascades (Strategy 24)

## Academic Foundation
- **Fee, Thomas (2004)**: *Sources of Gains in Horizontal Mergers: Evidence from Customer, Supplier, and Rival Firms* (Journal of Financial Economics)
- **Menzly, Ozbas (2010)**: *Market Segmentation and Cross-Predictability of Returns* (Journal of Finance)
- **Barrot, Sauvagnat (2016)**: *Input Specificity and the Propagation of Idiosyncratic Shocks* (Quarterly Journal of Economics)

## Quantitative Alpha Mechanics
Captures supply chain earnings diffusion lags and inventory bottleneck signals where downstream customer demand shocks propagate into upstream suppliers with structural multi-week delays.
- **Turnover Target**: < 12% via `ts_decay_linear(decay=14-20)`.
- **Fitness Invariant**: ≥ 1.00 via volume conviction gating (`volume > adv20 * 0.8`).
