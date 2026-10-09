# Strategy: Synthetic Forward Basis Spread

Cross-sectional forward-to-spot basis dispersion predicts equity drift over 20–60 day holding horizons.

Under put-call parity, synthetic forward prices reflect market expectations of future spot levels including dividend adjustments and carry financing rates. Persistent cross-sectional dispersion in forward-to-spot basis — driven by dividend yield surprises, borrow cost asymmetries, and rate expectation mismatches — predicts equity return drift. Stocks where the implied forward price diverges materially from carry-model estimates exhibit abnormal returns over 20 to 60-day windows.

## Mechanism

**Implied forward basis spread:**

$$\text{ForwardBasis}_t = \text{SynthFwdPrice}_t - \text{CarryModelFwd}_t$$

$$\alpha_{\text{FwdBasis}} = \text{group\_neutralize}\left(\text{rank}\left(\text{ts\_decay\_linear}\left(\frac{\text{synth\_fwd\_basis}_t}{\text{close}_t},\ 10\right)\right),\ \text{subindustry}\right)$$

*Worked example:* A stock trading at 100 with a synthetic forward of 103 and carry-model forward of 101 has a basis spread of +2. Ranked cross-sectionally and decay-smoothed, this positive basis signals near-term upward drift — the market prices in an above-carry expectation.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP2000`, `TOP1000`, `TOP3000` |
| Holding decay | 18–26 days |
| Neutralizations | `SUBINDUSTRY`, `SECTOR` |
| Data fields | `synth_fwd_basis`, `fwd_spot_basis_ratio`, `call_breakeven_cost` |

## Academic Basis

- **Derman & Miller (2016):** Synthetic forward parity as the no-arbitrage anchor for options surface construction; basis as dividend/rate surprise proxy.
- **Carr & Wu (2009):** Forward price divergence from carry model as a variance risk signal embedded in the options surface.
- **Natenberg (2014):** At-the-forward vs at-the-money distinction; basis sign flips with dividend/carry mismatch.

## Testing

```bash
python -m pytest tests/ -v -k forward_basis
python -m brain_options.run --single-batch --strategy forward_basis
```
