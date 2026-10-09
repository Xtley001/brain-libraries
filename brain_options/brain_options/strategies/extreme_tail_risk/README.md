# Strategy: Extreme Tail Risk & OTM Put Smirk

Volatility smirk steepness measures jump disaster pricing and predicts equity underperformance.

The volatility smirk in individual equity options captures the market's pricing of negative jump risk. Under the Bakshi, Kapadia & Madan (2003) framework, the difference in implied volatility between out-of-the-money puts and at-the-money calls directly measures higher-order moments — risk-neutral skewness and kurtosis. Firms with the steepest smirks underperform those with flatter smirks by over 10% annualized, as sophisticated investors bid up protective puts ahead of firm-specific negative shocks.

## Mechanism

**Smirk asymmetry signal:**

$$\text{Smirk}_t = \text{IV}_{25\Delta\text{put},\, t} - \text{IV}_{50\Delta\text{call},\, t}$$

$$\alpha_{\text{TailRisk}} = -\text{group\_neutralize}\left(\text{ts\_zscore}(\text{Smirk}_t,\ 60),\ \text{subindustry}\right)$$

**Surface convexity extension:**

$$\alpha_{\text{Convexity}} = -\text{group\_rank}(\text{SurfaceConvexity}_t,\ \text{industry})$$

*Worked example:* A stock with 25-delta put IV of 0.35 and ATM call IV of 0.25 has Smirk = +0.10. If this is elevated relative to the 60-day history (ts_zscore > +1.5), the alpha assigns a negative (short) score after neutralization — stock is expected to underperform.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP1000`, `TOP2000`, `TOP3000` |
| Holding decay | 14–22 days |
| Neutralizations | `SUBINDUSTRY`, `INDUSTRY` |
| Data fields | `iv_skew_25d_put`, `iv_atm_call_30`, `skew_smirk` |

## Academic Basis

- **Bakshi, Kapadia & Madan (2003):** Model-free skewness and kurtosis from option prices; OTM put premium reflects jump risk pricing.
- **Xing, Zhang & Zhao (2010):** Steepest-smirk quintile underperforms flattest-smirk quintile by 10%+ annualized in individual equities.
- **Bennett (2014):** Practical construction of vol surface asymmetry signals from 25-delta put vs ATM call IV.

## Testing

```bash
python -m pytest tests/ -v -k extreme_tail_risk
python -m brain_options.run --single-batch --strategy extreme_tail_risk
```
