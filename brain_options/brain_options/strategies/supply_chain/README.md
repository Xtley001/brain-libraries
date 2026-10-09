# Strategy: Supply Chain Shock Propagation & Customer-Supplier Lead-Lag

Idiosyncratic shocks to upstream suppliers propagate to downstream customer stocks with 5–20-day delay.

Modern industrial firms operate within tightly coupled input-output production networks. Idiosyncratic shocks — disruptions, natural disasters, input price spikes, or earnings surprises — originating in upstream supplier firms propagate downstream to customer firms with measurable time delays (5 to 20 trading days), primarily due to investor inattention and delayed customer supply renegotiations. Barrot & Sauvagnat (2016) and Cohen & Frazzini (2008) document this predictable cross-industry return lead-lag.

## Mechanism

Let firm $i$ belong to supplier industry $I_{\text{sup}}$ and firm $j$ belong to customer industry $I_{\text{cust}}$:

**Supplier earnings shock propagation:**

$$\text{SupplierShock}_{I_{\text{sup}}, t} = \text{group\_mean}(\text{eps\_surprise},\ \text{supplier\_industry})$$

$$\alpha_{\text{SupplyChain}} = \text{group\_neutralize}\left(\text{rank}\left(\text{ts\_delay}(\text{SupplierShock}_{I_{\text{sup}}, t},\ 10)\right),\ \text{customer\_industry}\right)$$

*Worked example:* If semiconductor suppliers (upstream) report negative EPS surprises this week, the signal applies a lagged negative score to electronics assemblers (downstream customers) 10 trading days later — the market has not yet priced the cost shock into the customer's forward earnings.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP2000`, `TOP3000`, `TOP1000` |
| Holding decay | 14–22 days |
| Propagation delay | 5–20 trading days (`ts_delay`) |
| Neutralizations | `INDUSTRY`, `SECTOR` |
| Data fields | `eps_surprise`, `returns`, `revenue_surprise` |

## Academic Basis

- **Barrot & Sauvagnat (2016):** Input specificity and production network shock propagation — disasters to key suppliers cause –3.5% to –5% cumulative abnormal returns in customer firms.
- **Cohen & Frazzini (2008):** Economic links and predictable returns — stocks of customer firms are predictable from supplier firms' returns with 1-month delay.

## Testing

```bash
python -m pytest tests/ -v -k supply_chain
python -m brain_options.run --single-batch --strategy supply_chain
```
