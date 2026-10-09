# Strategy: Put-Call Ratio & Order Flow Imbalances

Unusual option volume spikes relative to open interest predict directional equity price discovery.

Institutional option market participants possess superior private information and trade aggressively in out-of-the-money put and call options prior to major corporate announcements and macro shifts. Unusual spikes in trading volume relative to existing open interest extract liquidity concessions from dealers, providing high-conviction directional signals. Pan & Poteshman (2006) demonstrate that buyer-initiated put-call volume ratios predict next-day and 5–20-day forward equity returns with statistically significant effect sizes.

## Mechanism

**Pan-Poteshman flow velocity:**

$$\alpha_{\text{InformedFlow}} = \text{ts\_decay\_linear}\left(-\frac{\text{pcr\_vol}_t}{\text{pcr\_oi}_t + 0.001},\ 5\right)$$

Conditioned on underlying equity liquidity:

$$\alpha_{\text{PCR}} = \text{trade\_when}\left(\text{volume} > \text{adv20},\ \text{group\_neutralize}\left(\text{rank}(\alpha_{\text{InformedFlow}}),\ \text{subindustry}\right),\ -1\right)$$

*Worked example:* A stock with `pcr_vol` = 1.8 and `pcr_oi` = 0.9 has a flow ratio of 2.0 — unusually bearish. The 5-day decay score is negative; after subindustry neutralization, this stock goes short. The `adv20` gate ensures only high-liquidity names are included.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP2000`, `TOP3000`, `TOP1000` |
| Holding decay | 10–18 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Liquidity gate | `volume > adv20` |
| Data fields | `pcr_oi_ratio`, `pcr_volume_ratio`, `put_volume_surge`, `call_volume_surge` |

## Academic Basis

- **Pan & Poteshman (2006):** Buyer-initiated put-call ratios in public customer data predict stock returns; low PCR → positive returns, high PCR → negative returns.
- **Garleanu, Pedersen & Poteshman (2009):** Demand-based option pricing — net option demand drives implied volatility and signals future returns.

## Testing

```bash
python -m pytest tests/ -v -k pcr_flow
python -m brain_options.run --single-batch --strategy pcr_flow
```
