# Strategy: WorldQuant Formulaic Alpha Synthesis

Canonical price-volume microstructure interactions from the 101 Formulaic Alphas corpus.

Kakushadze (2015) published 101 quantitative expressions historically deployed by WorldQuant. These alphas exploit non-linear price-volume relationships, cross-sectional ranking, time-series decay functions, and liquidity interactions. Unlike fundamental or static factor models, formulaic alphas capture transient microstructural order imbalances, liquidity exhaustion, and geometric relative positioning — providing uncorrelated diversification across all other strategy pillars.

## Mechanism

**Alpha #6 — Liquidity exhaustion reversal:**

$$\alpha_6 = -\text{group\_neutralize}\left(\text{rank}\left(\text{ts\_corr}(\text{open},\ \text{volume},\ 10)\right),\ \text{subindustry}\right)$$

**Alpha #41 — Geometric range skew:**

$$\alpha_{41} = \text{group\_neutralize}\left(\text{rank}\left(\sqrt{\text{high} \times \text{low}} - \text{vwap}\right),\ \text{subindustry}\right)$$

**Alpha #54 — Volume-weighted extremes:**

$$\alpha_{54} = -\text{group\_rank}(\text{ts\_rank}(\text{volume},\ 20),\ \text{industry}) \times \text{group\_rank}(\text{ts\_delta}(\text{close},\ 5),\ \text{industry})$$

*Worked example (Alpha #41):* A stock with high = 105, low = 95 has geometric mean = √(105 × 95) ≈ 99.97. If VWAP = 101, then (99.97 – 101) = –1.03 — below VWAP geometric mean, signaling short-term distribution pressure.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP3000`, `TOP2000` |
| Holding decay | 5–15 days |
| Neutralizations | `SUBINDUSTRY`, `INDUSTRY` |
| Data fields | `open`, `close`, `high`, `low`, `volume`, `vwap`, `adv20` |

## Academic Basis

- **Kakushadze (2015):** *101 Formulaic Alphas* — 101 live WorldQuant expressions across price, volume, and cross-sectional ranking operators.
- **Tulchinsky et al. (2019):** *Finding Alphas* — institutional methodology for constructing and testing price-volume cross-sectional signals at scale.

## Testing

```bash
python -m pytest tests/ -v -k formulaic_101
python -m brain_options.run --single-batch --strategy formulaic_101
```
