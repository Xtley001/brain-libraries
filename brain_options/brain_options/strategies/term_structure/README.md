# Strategy: Volatility Term Structure & Variance Risk Premium

IV term structure inversions and the variance risk premium predict equity and volatility mean-reversion.

Option implied volatility systematically overprices expected realized variance due to institutional demand for downside tail insurance. This overpricing — the Variance Risk Premium (VRP) — is harvested by selling volatility when the IV term structure inverts ($IV_{30} > IV_{90}$), signaling temporary event panic that reliably mean-reverts. Carr & Wu (2009) demonstrate that the VRP is quadratic in implied volatility; Sinclair (2013) shows that mean-reversion entries are optimal when volatility crosses 0.75 standard deviations from its rolling mean.

## Mechanism

**Variance risk premium signal:**

$$\text{VRP}_t = \text{iv\_atm\_call\_30}_t - \text{ts\_mean}(\text{realized\_vol\_30}_t,\ 30)$$

$$\alpha_{\text{VRP}} = -\text{group\_neutralize}\left(\text{rank}\left(\text{ts\_zscore}(\text{VRP}_t,\ 60)\right),\ \text{subindustry}\right)$$

**Term structure inversion signal:**

$$\text{TermSlope}_t = \text{iv\_atm\_call\_30}_t - \text{iv\_atm\_call\_90}_t$$

$$\alpha_{\text{TermInv}} = -\text{group\_neutralize}\left(\text{rank}\left(\text{ts\_decay\_linear}(\text{TermSlope}_t,\ 5)\right),\ \text{subindustry}\right)$$

*Worked example:* A stock with 30-day IV = 0.45 and 90-day IV = 0.32 has term slope = +0.13 — inverted (short-term panic premium). The decay-smoothed inversion score is positive, and after negation and neutralization, the stock goes short on the vol-selling signal, capturing the mean-reversion of elevated near-term IV.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP1000`, `TOP3000`, `TOP2000` |
| Holding decay | 20–30 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Data fields | `iv_atm_call_30`, `iv_atm_call_60`, `iv_atm_call_90`, `vol_term_slope` |

## Academic Basis

- **Carr & Wu (2009):** Synthetic variance swap replication; VRP is a robust and persistent risk premium across equity index and single-stock options.
- **Sinclair (2013):** Mean-reverting volatility models — optimal entry at 0.75 SD above rolling mean; term structure inversion as a tactical signal.
- **Bennett (2014):** Practical construction of vol term structure signals; inversion as a short-vol entry trigger.

## Testing

```bash
python -m pytest tests/ -v -k term_structure
python -m brain_options.run --single-batch --strategy term_structure
```
