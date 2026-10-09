# Strategy: Informed Short Demand vs Loan Supply Friction

Separating institutional short demand shifts from lender supply contractions isolates the strongest bearish signal.

Traditional short interest metrics conflate outward shifts in short seller demand with contractions in institutional share supply (custodian recalls, float restrictions). Engelberg, Reed & Ringgenberg (2012) and Cohen, Diether & Malloy (2007) demonstrate that separating demand shifts from supply shifts generates significantly stronger, more persistent alpha: when borrow demand spikes concurrent with high utilization, stocks experience pronounced negative drift of 15%+ annualized.

## Mechanism

Let borrow demand shock $\Delta D_t$ be proxied by short rate of change, and supply friction $S_t$ by loan utilization and lendable inventory:

**Demand × supply interaction:**

$$\alpha_{\text{Informed}} = \text{group\_neutralize}\left(\text{rank}\left(-\text{ts\_delta}(\text{borrow\_fee},\ 5) \times \text{ts\_delta}\left(\frac{\text{short\_interest}}{\text{float\_shares} + 0.001},\ 10\right)\right),\ \text{subindustry}\right)$$

**Utilization gated signal:**

$$\alpha_{\text{Friction}} = \text{group\_neutralize}\left(\text{rank}\left(-\text{ts\_decay\_linear}\left(\text{loan\_utilization} \times \text{borrow\_fee},\ 10\right)\right),\ \text{subindustry}\right)$$

*Worked example:* A stock where borrow fee rises by 0.50% over 5 days and short interest ratio rises by 0.02 produces a demand × supply score of –0.50 × 0.02 = –0.01. Ranked cross-sectionally, this negative score places the stock in the short book.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP500`, `TOP1000`, `TOPSP500` |
| Holding decay | 14–22 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Liquidity gate | `volume > adv20` |
| Data fields | `borrow_fee`, `short_interest`, `float_shares`, `loan_utilization` |

## Academic Basis

- **Cohen, Diether & Malloy (2007):** Demand-shift identification — outward shifts in borrow demand predict –15%+ annualized returns.
- **Engelberg, Reed & Ringgenberg (2012):** Short sellers are informed; their demand shocks predict large subsequent negative abnormal returns.
- **Asquith, Pathak & Ritter (2005):** Short interest × institutional ownership interaction predicts underperformance.

## Testing

```bash
python -m pytest tests/ -v -k informed_short_demand
python -m brain_options.run --single-batch --strategy informed_short_demand
```
