# Strategy: Analyst Consensus Revisions & PEAD

Earnings estimate drift and post-announcement momentum predict equity returns 30–60 days forward.

Sell-side analysts adjust forecasts slowly due to cognitive anchoring, institutional friction, and reputational risk. When consensus revisions turn sharply positive, prices drift for 30 to 60 trading days. Wide analyst disagreement reflects high uncertainty; under short-sale constraints, high-dispersion stocks become overpriced and subsequently underperform.

## Mechanism

**Consensus revision momentum:**

$$\alpha_{\text{rev}} = \text{group\_neutralize}\left(\text{rank}\left(\text{ts\_decay\_linear}\left(\frac{\text{est\_eps}_t - \text{est\_eps}_{t-30}}{|\text{est\_eps}_{t-30}| + 0.01}, 10\right)\right), \text{subindustry}\right)$$

**Dispersion fade (short high-disagreement stocks):**

$$\alpha_{\text{disp}} = -\text{group\_neutralize}\left(\text{rank}\left(\text{ts\_zscore}\left(\frac{\text{std\_dev\_eps\_est}}{|\text{est\_eps}| + 0.01}, 60\right)\right), \text{sector}\right)$$

*Worked example:* A stock with `est_eps` rising from 1.00 to 1.15 over 30 days scores +0.15 / 1.01 ≈ +0.149 raw revision momentum. After subindustry neutralization and ranking, it occupies the upper quartile of the long book.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOPSP500`, `TOP500`, `TOP1000` |
| Holding decay | 18–30 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR`, `INDUSTRY` |
| Gate on | `num_analysts >= 3` to avoid noisy single-analyst estimates |

## Academic Basis

- **Givoly & Lakonishok (1979):** Analysts update forecasts in autocorrelated clusters over 15–60 days; positive revision ratio signals positive drift.
- **Diether, Malloy & Scherbina (2002):** High analyst disagreement predicts underperformance; short-sale constraints force price to reflect only optimistic views.
- **Bernard & Thomas (1989, 1990):** Post-earnings-announcement drift is delayed and persistent — investors under-react to earnings surprises.
- **Martineau (2021):** Modern information diffusion compresses but does not eliminate PEAD in large-cap universes.

## Testing

```bash
python -m pytest tests/ -v -k analyst_revisions
python -m brain_options.run --single-batch --strategy analyst_revisions
```
