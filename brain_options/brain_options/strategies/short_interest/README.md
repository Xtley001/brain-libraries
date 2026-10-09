# Strategy: Short Interest & Borrow Squeeze Dynamics

Borrow fee spikes against constrained lending supply signal forced short covering and violent directional moves.

Aggregate short interest is one of the strongest cross-sectional predictors of equity returns. When short demand surges against constrained lending supply — manifesting as elevated borrow fees and high utilization — stocks experience significant subsequent downward drift. Conversely, when highly shorted stocks experience sudden upward volume breakouts, trapped shorts are forced to cover, triggering sharp explosive rallies. Both dynamics generate exploitable alpha.

## Mechanism

**Borrow fee × utilization signal:**

$$\alpha_{\text{BorrowSqueeze}} = \text{group\_neutralize}\left(\text{rank}\left(-\text{ts\_decay\_linear}(\text{borrow\_fee}_t \times \text{loan\_utilization}_t,\ 10)\right),\ \text{subindustry}\right)$$

**Days-to-cover squeeze pressure:**

$$\alpha_{\text{DTC}} = \text{group\_neutralize}\left(\text{rank}\left(-\text{ts\_zscore}(\text{days\_to\_cover}_t,\ 60)\right),\ \text{subindustry}\right)$$

*Worked example:* A stock with borrow fee = 4.5% and loan utilization = 0.88 scores 4.5 × 0.88 = 3.96. If this is elevated vs its 10-day decay average, the alpha assigns a short score. After subindustry neutralization, this stock is in the bottom decile (short book) — expected to decline as the borrow cost discourages new shorts while supply tightens.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP500`, `TOP1000`, `TOPSP500` |
| Holding decay | 16–24 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Data fields | `borrow_fee_spike`, `loan_utilization_ratio`, `days_to_cover`, `short_interest` |

## Academic Basis

- **Asquith, Pathak & Ritter (2005):** Short interest × institutional ownership predicts strong underperformance; borrow availability moderates squeeze risk.
- **Rapach, Ringgenberg & Zhou (2016):** Aggregate short interest predicts market returns; de-trended stock-level short interest z-scores predict cross-sectional returns.
- **Cohen, Diether & Malloy (2007):** Demand-side shifts in shorting markets — borrow fee spikes driven by demand predict –15%+ annualized abnormal returns.

## Testing

```bash
python -m pytest tests/ -v -k short_interest
python -m brain_options.run --single-batch --strategy short_interest
```
