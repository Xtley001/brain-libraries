# Strategy: Network Graph Clustering & Co-Movement Lead-Lag Momentum

Assets diverging from their cluster centroid provide high-Sharpe mean-reverting alpha.

Financial markets exhibit community clustering architectures where assets in the same industrial or correlation cluster share common underlying risk factors. As formulated by Lopez de Prado (2018) in Hierarchical Risk Parity literature, asset returns decompose into a cluster centroid component and an idiosyncratic residual. Assets exhibiting short-term divergence from their cluster centroid provide high-Sharpe mean-reverting alpha, while the cluster centroid itself provides directional momentum — two distinct signals from the same network structure.

## Mechanism

Let $\mathcal{C}_k$ be the peer community cluster (subindustry or industry group) for asset $i$:

**Cluster mean-reversion signal:**

$$\text{ClusterCentroid}_{k,t} = \text{group\_mean}(\text{returns},\ \text{subindustry})$$

$$\alpha_{\text{MeanRev}} = \text{group\_neutralize}\left(\text{rank}\left(-\text{ts\_zscore}(\text{returns}_t - \text{ClusterCentroid}_{k,t},\ 10)\right),\ \text{subindustry}\right)$$

**Centroid momentum lead-lag:**

$$\alpha_{\text{Momentum}} = \text{group\_neutralize}\left(\text{rank}\left(\text{ts\_decay\_linear}(\text{ClusterCentroid}_{k,t-5},\ 10)\right),\ \text{subindustry}\right)$$

*Worked example:* A stock that has returned –3% over 5 days while its subindustry centroid returned +1% shows an idiosyncratic deviation of –4%. The ts_zscore of this gap over 10 days is negative — the stock is oversold relative to its cluster and goes long on the mean-reversion signal.

## Execution Parameters

| Parameter | Value |
|---|---|
| Universes | `TOP1000`, `TOP2000`, `TOP3000` |
| Holding decay | 10–20 days |
| Neutralizations | `SUBINDUSTRY`, `INDUSTRY` |
| Data fields | `returns`, `close`, `volume` |
| Cluster proxy | `subindustry`, `industry` group operators |

## Academic Basis

- **Lopez de Prado (2018):** Hierarchical Risk Parity and cluster-based portfolio construction; asset co-movement within network communities.
- **Tulchinsky et al. (2019):** Cross-sectional momentum and mean-reversion within industry clusters as a source of persistent alpha.

## Testing

```bash
python -m pytest tests/ -v -k network_momentum
python -m brain_options.run --single-batch --strategy network_momentum
```
