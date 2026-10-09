# Brain Synthesis — WorldQuant BRAIN Data Dictionary

> Author: [Xtley001](https://github.com/Xtley001)  
> Repository: [brain-alpha-pipeline](https://github.com/Xtley001/brain-libraries)  
> Version: 0.1.0

This document specifies every WorldQuant BRAIN platform data field referenced across the `brain_synthesis` library and its 5 Golden Apex Formulations.

---

## 1. Dataset Dependencies Overview

The `brain_synthesis` engine achieves orthogonal alpha fusion by combining three distinct institutional data families:

| Leg | Data Family | WorldQuant Datasets | ValueScore |
|---|---|---|---|
| **Leg 1** | Options Implied & Surface Derivatives | `option8`, `option9` | 6.0 |
| **Leg 2** | Analyst Sentiment & Consensus Revisions | `sentiment1`, `sentiment2` | 8.0 |
| **Leg 3** | Systematic Risk Models & Factor Premia | `model51`, `model52` | 7.0 |

> [!IMPORTANT]
> To execute simulations using these expressions on the WorldQuant BRAIN platform, your BRAIN user account must have read permissions enabled for the `option8`, `sentiment1`, and `model51` data subscriptions.

---

## 2. Field Specifications

### 2.1 Options Surface & Breakeven Fields (Leg 1)

#### `forward_price_60`, `forward_price_90`, `forward_price_120`
- **Dataset:** `option8` / `option9`
- **Type:** MATRIX (float)
- **Description:** Implied forward equity price projected at 60, 90, and 120 calendar days forward, derived from put-call parity and interest-rate/dividend yield curves.
- **Economic Rationale:** Represents the market-implied risk-neutral expected price at future option expiration cycles.

#### `put_breakeven_60`, `put_breakeven_90`, `put_breakeven_120`
- **Dataset:** `option8` / `option9`
- **Type:** MATRIX (float)
- **Description:** Downside breakeven price for at-the-money or delta-standardized put contracts ($K - P$) at 60, 90, and 120-day expiries.
- **Formula Usage:** `(forward_price_60 - put_breakeven_60) / close`
- **Economic Rationale:** Measures the width of institutional downside insurance support. A widening cushion relative to the current stock price signals strong institutional put writing and structural price floors.

#### `call_breakeven_90`
- **Dataset:** `option8` / `option9`
- **Type:** MATRIX (float)
- **Description:** Upside breakeven price for call options ($K + C$) at 90 days.
- **Formula Usage:** `(call_breakeven_90 - forward_price_90) / close`
- **Economic Rationale:** Measures the upside hurdle rate required for call buyers to achieve profitability, capturing market sentiment toward aggressive upside expansion.

#### `implied_volatility_mean_30`, `implied_volatility_mean_60`, `implied_volatility_mean_180`
- **Dataset:** `option8` / `option9`
- **Type:** MATRIX (float)
- **Description:** At-the-money implied volatility level at 30, 60, and 180 calendar days.
- **Formula Usage:** `implied_volatility_mean_180 - implied_volatility_mean_30`
- **Economic Rationale:** Volatility term structure slope. Upward-sloping term structure (contango) reflects normal risk premium; downward-sloping (backwardation) signals acute short-term event risk.

#### `implied_volatility_put_60`, `implied_volatility_call_60`
- **Dataset:** `option8`
- **Type:** MATRIX (float)
- **Description:** Implied volatility of standardized 25-delta put and 25-delta call options at 60-day expiry.
- **Formula Usage:** `-(implied_volatility_put_60 - implied_volatility_call_60) / (implied_volatility_mean_60 + 0.001)`
- **Economic Rationale:** Implied volatility smirk / skew inversion. Quantifies the premium charged for tail downside insurance over upside participation. Reversion occurs after panic peaks.

---

### 2.2 Analyst Sentiment & Revision Fields (Leg 2)

#### `snt1_d1_netearningsrevision`
- **Dataset:** `sentiment1`
- **Type:** MATRIX (float)
- **Description:** Daily net revision ratio of Wall Street consensus earnings per share (EPS) estimates ($\frac{\text{Upgrades} - \text{Downgrades}}{\text{Total Revisions}}$).
- **Economic Rationale:** Post-Earnings Announcement Drift (PEAD). Sell-side analysts revise forecasts incrementally due to career-risk conservatism, causing predictable multi-month price drift.

#### `snt1_d1_earningssurprise`
- **Dataset:** `sentiment1`
- **Type:** MATRIX (float)
- **Description:** Standardized Unexpected Earnings (SUE) shock on announcement day: percentage deviation of reported EPS from median consensus estimate.
- **Economic Rationale:** Fundamental information shock. Positive surprises trigger persistent institutional capital reallocation over 20–60 trading days.

#### `snt1_d1_nettargetpercent`
- **Dataset:** `sentiment1`
- **Type:** MATRIX (float)
- **Description:** Consensus 12-month price target percentage change over the last observation period.
- **Economic Rationale:** Measures structural equity valuation adjustments by sell-side research teams.

#### `snt1_d1_earningstorpedo`
- **Dataset:** `sentiment1`
- **Type:** MATRIX (float)
- **Description:** Proprietary risk indicator estimating extreme downside revision vulnerability ahead of corporate earnings announcements.
- **Economic Rationale:** Flags stocks where sell-side expectations are unrealistically elevated and vulnerable to severe valuation compression.

#### `snt1_d1_dynamicfocusrank`
- **Dataset:** `sentiment1`
- **Type:** MATRIX (float)
- **Description:** Cross-sectional ranking of institutional analyst attention and coverage velocity.
- **Economic Rationale:** Attention asymmetry: signals receiving focused coverage exhibit faster price discovery and reduced noise.

---

### 2.3 Systematic Risk & Factor Fields (Leg 3)

#### `beta_last_60_days_spy`, `beta_last_90_days_spy`
- **Dataset:** `model51` / `model52`
- **Type:** MATRIX (float)
- **Description:** Rolling 60-day and 90-day ordinary least squares (OLS) equity return beta against the S&P 500 ETF (SPY).
- **Formula Usage:** Subtracted with negative weight (`-0.20 * rank(ts_decay_linear(beta_last_60_days_spy, d))`)
- **Economic Rationale:** Frazzini & Pedersen (2014) Betting-Against-Beta (BAB) anomaly. Constrained institutional investors bid up high-beta stocks, depressing their risk-adjusted returns and creating structural alpha in low-beta assets.

#### `correlation_last_60_days_spy`
- **Dataset:** `model51` / `model52`
- **Type:** MATRIX (float)
- **Description:** 60-day rolling Pearson correlation coefficient against SPY.
- **Economic Rationale:** Filters for idiosyncratic returns with minimal systematic market exposure, critical for passing the BRAIN correlation gate.

#### `fscore_surface_accel`, `fscore_bfl_quality`
- **Dataset:** `model51` / `model52`
- **Type:** MATRIX (float)
- **Description:** Piotroski F-Score acceleration and balance-sheet financial quality factor metrics.
- **Economic Rationale:** Financial strength conditioning: ensures signal momentum is backed by improving operating cash flows and balance-sheet solvency rather than leverage.

---

## 3. The 5 Golden Apex Formulations

| Formulation | Name | Core Signal | Target Horizon |
|---|---|---|---|
| **Apex 1** | Accumulation Triple | Put Floor (50%) + Analyst Revisions (30%) + Low SPY Beta (20%) | 10–15 days |
| **Apex 2** | SUE Volatility Smirk | Skew Reversion (50%) + Earnings Shock (35%) + F-Score Quality (15%) | 10–15 days |
| **Apex 3** | Target Term Slope | IV Contango Slope (45%) + Target Price Revisions (35%) + Low Beta (20%) | 12–15 days |
| **Apex 4** | Torpedo Quality Drift | Torpedo Relief (40%) + Accounting Quality (35%) + Call Breakeven (25%) | 10–15 days |
| **Apex 5** | Attention Asymmetry | Forward Put Floor (40%) + Coverage Attention (30%) + Low SPY Corr (30%) | 12–15 days |
