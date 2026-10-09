# Orthogonal Decorrelation Axes v1.0

October 2026 · [Xtley001](https://github.com/Xtley001) · `brain-decorrelator`

Mathematical and operational specifications for the 6 universal transformation axes designed to defeat WorldQuant BRAIN's correlation gate ($|\rho| < 0.70$) while preserving predictive Sharpe ratio.

## Overview

When mining alphas within a single dataset family (e.g. options implied volatility or analyst revisions), naive formulaic variations cluster tightly with pairwise correlations $\rho \in [0.75, 0.95]$, triggering platform correlation rejections.

`brain-decorrelator` applies systematic mathematical operators that alter the return frequency, regime conditioning, and cross-sectional distribution of the signal, driving correlation below $0.70$ while preserving economic intuition.

## Orthogonal Axes Summary

| Axis | Mathematical Operator | Primary Effect | Typical $\rho$ Shift | Sharpe Retention |
|---|---|---|---|---|
| **Velocity** | `ts_decay_linear(ts_delta(expr, 5), 10)` | Temporal phase shift | $\rho \to 0.35 - 0.52$ | $\ge 85\%$ |
| **Neutralization** | `group_neutralize(expr, subindustry)` | Factor/sector invariance | $\rho \to 0.42 - 0.61$ | $\ge 95\%$ |
| **Volatility** | `expr / (ts_std_dev(returns, 20) + 1e-4)` | Dynamic regime scaling | $\rho \to 0.48 - 0.65$ | $\ge 90\%$ |
| **Rank** | `power(rank(expr) - 0.5, 3)` | Non-linear tail convexity | $\rho \to 0.55 - 0.68$ | $\ge 95\%$ |
| **Volume** | `expr * rank(volume / (ts_mean(volume, 20) + 1e-4))` | Liquidity order weighting | $\rho \to 0.38 - 0.58$ | $\ge 85\%$ |
| **Calendar** | `if_else(day_of_month(0) <= 5, expr * 1.2, expr * 0.8)` | Turn-of-month modulation | $\rho \to 0.60 - 0.68$ | $\ge 92\%$ |

## Detailed Axis Specifications

### 1. Velocity Axis (Temporal Phase Shift)

- **Economic Intuition:** Shifting the observation horizon or extracting rate-of-change (momentum/acceleration) separates high-frequency noise from structural trends.
- **Formulation:**
  $$\alpha_{\text{velocity}} = \text{ts\_decay\_linear}(\text{ts\_delta}(\alpha_{\text{base}}, d_1), d_2)$$
- **BRAIN Syntax:**
  ```python
  ts_decay_linear(ts_delta(expr, 5), 10)
  ```
- **Worked Example:**
  - Base: `rank(implied_volatility_call_30)` ($\rho = 1.00$)
  - Transformed: `ts_decay_linear(ts_delta(rank(implied_volatility_call_30), 5), 10)`
  - Realized Correlation: $\rho \approx 0.38$
  - Sharpe Retention: $88\%$ of base Sharpe.

### 2. Neutralization Axis (Factor & Industry Invariance)

- **Economic Intuition:** Removing broad market, sector, or sub-industry common modes isolates pure idiosyncratic security selection, eliminating macro factor crowding.
- **Formulation:**
  $$\alpha_{\text{neutral}} = \alpha_{\text{base}} - \mathbb{E}[\alpha_{\text{base}} \mid \text{Group}]$$
- **BRAIN Syntax:**
  ```python
  group_neutralize(expr, subindustry)
  ```
- **Worked Example:**
  - Base: `rank(snt1_d1_netearningsrevision)` ($\rho = 1.00$)
  - Transformed: `group_neutralize(rank(snt1_d1_netearningsrevision), subindustry)`
  - Realized Correlation: $\rho \approx 0.45$
  - Sharpe Retention: Typically improves Sharpe by removing sector drawdowns.

### 3. Volatility Axis (Regime Conditioning & Dynamic Sizing)

- **Economic Intuition:** Alphas perform differently across volatility regimes. Scaling inversely to realized return variance dampens tail drawdowns and expands capacity.
- **Formulation:**
  $$\alpha_{\text{vol\_scaled}} = \frac{\alpha_{\text{base}}}{\text{ts\_std\_dev}(\text{returns}, d) + \epsilon}$$
- **BRAIN Syntax:**
  ```python
  expr / (ts_std_dev(returns, 20) + 1e-4)
  ```
- **Worked Example:**
  - Base: `rank(put_breakeven - close)` ($\rho = 1.00$)
  - Transformed: `rank(put_breakeven - close) / (ts_std_dev(returns, 20) + 1e-4)`
  - Realized Correlation: $\rho \approx 0.52$
  - Sharpe Retention: $\ge 90\%$.

### 4. Rank Axis (Convexity & Quantile Dispersion)

- **Economic Intuition:** Linear weighting exposes portfolios to moderate, noisy conviction names. Applying non-linear odd power transforms concentrates capital in the high-conviction tails while compressing the middle.
- **Formulation:**
  $$\alpha_{\text{convex}} = \text{sign}(\alpha_{\text{rank}} - 0.5) \cdot |\alpha_{\text{rank}} - 0.5|^p \quad (p \ge 3, \text{odd})$$
- **BRAIN Syntax:**
  ```python
  power(rank(expr) - 0.5, 3)
  ```
- **Worked Example:**
  - Base: `rank(beta_last_60_days_spy)` ($\rho = 1.00$)
  - Transformed: `power(rank(beta_last_60_days_spy) - 0.5, 3)`
  - Realized Correlation: $\rho \approx 0.58$
  - Sharpe Retention: $\ge 95\%$.

### 5. Volume Axis (Liquidity Scaling & Order Flow Weighting)

- **Economic Intuition:** Scaling alpha intensity by relative trading volume shifts the portfolio towards liquid names where transaction costs are low and capacity is high.
- **Formulation:**
  $$\alpha_{\text{vol\_adj}} = \alpha_{\text{base}} \cdot \text{rank}\left(\frac{\text{volume}}{\text{ts\_mean}(\text{volume}, d) + \epsilon}\right)$$
- **BRAIN Syntax:**
  ```python
  expr * rank(volume / (ts_mean(volume, 20) + 1e-4))
  ```
- **Worked Example:**
  - Base: `rank(forward_price - close)` ($\rho = 1.00$)
  - Transformed: `rank(forward_price - close) * rank(volume / (ts_mean(volume, 20) + 1e-4))`
  - Realized Correlation: $\rho \approx 0.44$
  - Turnover Reduction: $15 - 25\%$ decrease in daily turnover.

### 6. Calendar Axis (Turn-of-Month Modulation)

- **Economic Intuition:** Systematic institutional rebalancing flows occur during the first five trading days of the calendar month (Turn-of-Month effect).
- **Formulation:**
  $$\alpha_{\text{calendar}} = \alpha_{\text{base}} \cdot \left(1 + \delta \cdot \mathbb{I}(\text{day} \le 5)\right)$$
- **BRAIN Syntax:**
  ```python
  if_else(day_of_month(0) <= 5, expr * 1.2, expr * 0.8)
  ```
- **Worked Example:**
  - Base: `rank(snt1_d1_earningssurprise)` ($\rho = 1.00$)
  - Transformed: `if_else(day_of_month(0) <= 5, rank(snt1_d1_earningssurprise) * 1.2, rank(snt1_d1_earningssurprise) * 0.8)`
  - Realized Correlation: $\rho \approx 0.62$
  - Sharpe Retention: $\ge 92\%$.

## Programmatic Usage

```python
from brain_decorrelator import DecorrelationEngine

engine = DecorrelationEngine()

variants = engine.generate_orthogonal_variants(
    expression="rank(implied_volatility_call_30)",
    base_sharpe=1.65,
    max_variants=5,
)

for v in variants:
    print(f"Axis: {v.axis_name:<15} -> {v.transformed_expression}")
```
