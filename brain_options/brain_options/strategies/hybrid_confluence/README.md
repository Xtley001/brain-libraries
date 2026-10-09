# Strategy: Cross-Asset Hybrid Confluence

Multi-factor confluence of options skew, borrow fee, and analyst revisions delivers orthogonal alpha with minimal market beta.

Asset prices do not adjust instantaneously across fragmented financial markets. Options market participants frequently trade ahead of cash equity participants, while equity lending supply (borrow fees) reflects institutional conviction that equity analysts take weeks to digest. Cross-asset hybrid confluence synthesizes orthogonal signals from all three dimensions — delivering higher Sharpe ratios and minimal market factor beta precisely because each component captures a distinct information lag.

## Mechanism

**Three-factor confluence signal:**

$$\alpha_{\text{Skew}} = -\text{ts\_zscore}(\text{skew\_smirk}_t,\ 20)$$

$$\alpha_{\text{Borrow}} = -\text{ts\_zscore}(\text{borrow\_fee}_t,\ 20)$$

$$\alpha_{\text{Rev}} = \text{ts\_decay\_linear}\left(\frac{\text{est\_eps}_t - \text{est\_eps}_{t-20}}{|\text{est\_eps}_{t-20}| + 0.01},\ 10\right)$$

$$\alpha_{\text{Confluence}} = \text{group\_neutralize}\left(\text{rank}\left(\alpha_{\text{Skew}} + \alpha_{\text{Borrow}} + \alpha_{\text{Rev}}\right),\ \text{subindustry}\right)$$

*Worked example:* A stock with elevated put smirk (skew z-score = +1.8), rising borrow fee (borrow z-score = +1.5), and positive EPS revision (+0.12) scores positively on all three components. Combined and neutralized, this stock is in the top quintile of the long book.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOPSP500`, `TOP1000`, `TOP2000` |
| Holding decay | 18–26 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Data fields | `skew_smirk`, `borrow_fee`, `est_eps`, `short_interest` |

## Academic Basis

- **Garleanu, Pedersen & Poteshman (2009):** Demand-based option pricing — options skew reflects net informed hedging demand.
- **Cohen, Diether & Malloy (2007):** Borrow fee spikes signal informed institutional short demand.
- **Givoly & Lakonishok (1979):** Analyst revision clustering predicts 30–60-day forward drift.

## Testing

```bash
python -m pytest tests/ -v -k hybrid_confluence
python -m brain_options.run --single-batch --strategy hybrid_confluence
```
