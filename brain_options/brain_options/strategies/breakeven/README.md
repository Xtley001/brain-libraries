# Strategy: Call Breakeven Hurdle Acceleration

Call breakeven repricing vs realized volatility signals institutional repositioning ahead of directional equity breakouts.

The call breakeven price — strike plus option premium weighted across open interest — functions as the aggregate hurdle where call writers begin losing money. Shifting breakeven hurdles indicate institutional repositioning of upper gamma barriers prior to directional breakouts. Cross-sectional dispersion in breakeven-to-close ratio predicts equity drift over 16 to 24-day holding horizons.

## Mechanism

**Winsorized robust breakeven signal:**

$$\alpha_{\text{BE}} = \text{trade\_when}\left(\text{volume} > \text{adv20},\ \text{group\_neutralize}\left(\text{rank}\left(\text{ts\_decay\_linear}\left(\frac{\text{call\_breakeven}_t - \text{close}_t}{\text{close}_t},\ 5\right)\right),\ \text{subindustry}\right),\ -1\right)$$

*Worked example:* A stock trading at 100 with call breakeven at 108 has a ratio of +0.08. If this ratio has risen from +0.04 over 5 days (breakeven accelerating above spot), the 5-day decay-linear score is positive — stock goes long. Trade is gated to high-volume days (`volume > adv20`) to filter noise.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP500`, `TOP1000`, `TOP3000` |
| Holding decay | 16–24 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR`, `MARKET` |
| Liquidity gate | `volume > adv20` |

## Academic Basis

- **Natenberg (2014):** Call breakeven price as aggregate hurdle rate; options pricing in terms of breakeven volatility vs realized vol.
- **Sinclair (2013):** Breakeven repricing as a proxy for gamma repositioning and upcoming directional exposure.

## Testing

```bash
python -m pytest tests/ -v -k breakeven
python -m brain_options.run --single-batch --strategy breakeven
```
