# Strategy: Cross-Asset Implied Volatility Lead-Lag

Informed traders in the options market lead the cash equity market — IV innovations predict equity returns 10–20 days forward.

Informed traders with private information or superior analytical speed trade equity options before underlying cash equities due to embedded leverage, defined risk, and absence of short-sale borrow constraints. Bali & Hovakimian (2009) and Pan & Poteshman (2006) demonstrate that innovations in call vs put implied volatility and option volume imbalances predict underlying cash equity returns over 10 to 20-day forward windows with statistically significant and economically meaningful effect sizes.

## Mechanism

Let $\Delta\text{IV}_{\text{call}, 30, t}$ and $\Delta\text{IV}_{\text{put}, 30, t}$ be the 5-day changes in ATM call and put implied volatilities:

**Call-put IV spread innovation:**

$$\Delta\text{IV}_{\text{spread}, t} = \Delta\text{IV}_{\text{call}, 30, t} - \Delta\text{IV}_{\text{put}, 30, t}$$

$$\alpha_{\text{IVLeadLag}} = \text{group\_neutralize}\left(\text{rank}\left(\text{ts\_decay\_linear}(\Delta\text{IV}_{\text{spread}},\ 10)\right),\ \text{subindustry}\right)$$

*Worked example:* If ATM call IV rises from 0.28 to 0.31 (+0.03) while put IV stays flat, the spread innovation is +0.03. Cross-sectionally ranked and decay-smoothed, this positive spread innovation signals that informed call buyers anticipate upside — stock goes long.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP1000`, `TOP2000`, `TOP3000` |
| Holding decay | 10–20 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Data fields | `iv_atm_call_30`, `iv_atm_put_30`, `iv_atm_call_60`, `call_volume`, `put_volume` |

## Academic Basis

- **Bali & Hovakimian (2009):** Volatility spreads (call IV – put IV) predict future equity returns; realized-implied vol spread also predictive.
- **Pan & Poteshman (2006):** Informed option volume — buyer-initiated put-call ratios predict negative/positive equity returns over 5–20 days.
- **Garleanu, Pedersen & Poteshman (2009):** Demand-based option pricing framework; option flow imbalances as forward-looking cash equity signals.

## Testing

```bash
python -m pytest tests/ -v -k iv_lead_lag
python -m brain_options.run --single-batch --strategy iv_lead_lag
```
