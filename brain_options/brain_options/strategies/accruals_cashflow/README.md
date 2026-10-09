# Strategy: Accounting Quality & Accruals Anomaly

Operating cash flow divergence from reported earnings predicts subsequent return reversals.

The accrual anomaly, formulated by Sloan (1996), documents that the accrual component of earnings exhibits lower persistence than the cash flow component. Investors consistently overprice accruals and underprice operating cash flows, leading to predictable reversals as lower-quality earnings revert toward cash flow fundamentals. Cross-sectionally, stocks with high accruals underperform stocks with high cash flows by 10%+ annualized.

## Mechanism

**Sloan accrual spread:**

$$TA_t = \frac{\text{NetIncome}_t - \text{OperatingCashFlow}_t}{\text{TotalAssets}_t}$$

$$\alpha_{\text{Sloan}} = \text{rank}\left(\frac{\text{OperatingCashFlow}_t}{\text{TotalAssets}_t}\right) - \text{rank}\left(\frac{\text{NetIncome}_t}{\text{TotalAssets}_t}\right)$$

**Subindustry-neutralized:**

$$\alpha_{\text{AccrualNeutral}} = \text{group\_neutralize}\left(\alpha_{\text{Sloan}},\ \text{subindustry}\right)$$

*Worked example:* A company with Net Income = 50M, Operating Cash Flow = 30M, and Total Assets = 500M has TA = (50 – 30) / 500 = +0.04 — a high-accrual (lower quality) score, placing it in the short book.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOPSP500`, `TOP1000`, `TOP3000` |
| Holding decay | 20–30 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Data fields | `net_income`, `operating_cash_flow`, `total_assets` |

## Academic Basis

- **Sloan (1996):** Accrual component of earnings exhibits lower persistence than cash flow; documented 10%+ annual return spread.
- **Fabozzi, Focardi & Kolm (2010):** Quantitative implementation of accruals-based factors across liquid equity universes.
- **Grinold & Kahn (2000):** Cash flow quality as a fundamental alpha source in active portfolio management.

## Testing

```bash
python -m pytest tests/ -v -k accruals_cashflow
python -m brain_options.run --single-batch --strategy accruals_cashflow
```
