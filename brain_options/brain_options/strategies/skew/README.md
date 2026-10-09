# Strategy: Volatility Skew & Smirk Asymmetry

Downside implied volatility skew encodes private information and predicts cross-sectional equity returns.

Downside implied volatility skew measures the cost premium that option market makers charge for out-of-the-money put options compared to at-the-money calls. Institutional investors bid up put skew when possessing negative private information, hedging jump risk, or anticipating earnings shocks. Stocks with unusually steep smirks — proxied by 25-delta put IV vs 50-delta call IV — subsequently underperform their subindustry peers over 14 to 22-day holding horizons.

## Mechanism

**Square-root-time scaled smirk:**

$$\text{ScaledSkew}_t = \text{implied\_volatility\_mean\_skew}_t \times \sqrt{\frac{T}{252}}$$

This standardizes steepness across option expirations ($T$ = days to expiry).

**Cross-sectional smirk signal:**

$$\alpha_{\text{Skew}} = -\text{group\_neutralize}\left(\text{rank}\left(\text{ts\_zscore}(\text{skew\_smirk}_t,\ 20)\right),\ \text{subindustry}\right)$$

*Worked example:* A stock with 25-delta put IV of 0.38 and ATM call IV of 0.27 has smirk = +0.11. If the 20-day z-score of this smirk is +2.1, the alpha assigns a negative (short) score after neutralization — this stock is expected to underperform.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP1000`, `TOP2000`, `TOP3000` |
| Holding decay | 14–22 days |
| Neutralizations | `SUBINDUSTRY`, `INDUSTRY`, `SECTOR` |
| Data fields | `skew_smirk`, `skew_25d_vs_50d`, `iv_skew_call_put`, `implied_volatility_mean_skew` |

## Academic Basis

- **Bakshi, Kapadia & Madan (2003):** Model-free skewness from option prices; OTM put premium directly measures risk-neutral skewness.
- **Xing, Zhang & Zhao (2010):** Individual equity smirk predicts underperformance; steepest smirk quintile underperforms flattest by 10%+ annualized.
- **Garleanu, Pedersen & Poteshman (2009):** Net demand for downside puts drives the smirk via market maker inventory hedging.

## Testing

```bash
python -m pytest tests/ -v -k skew
python -m brain_options.run --single-batch --strategy skew
```
