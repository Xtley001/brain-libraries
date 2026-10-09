"""Formula templates for Options Expiration Gamma Pinning & Strike Clustering."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_gamma_pinning_clustering_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Delta Imbalance Forward Strike Pull
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(((forward_price_30 - close) / close) * (1.0 / (pcr_oi_30 + 0.001)), 12)), {grp}), -1)",
                archetype_name="Delta Imbalance Forward Pinning",
                hypothesis="Concentrated call open interest creates market maker dynamic delta hedging pull toward the forward strike price.",
                generation_source="template",
            )
        )

    # 2. Expiration Gamma Compression Reversal
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(ts_delta(implied_volatility_mean_30, 5), 10)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(ts_delta(close, 5) * (call_breakeven_30 / (forward_price_30 + 0.001) - 1.0), 15)), {grp}), -1)",
                archetype_name="Expiration Gamma Compression Magnet",
                hypothesis="Rapid IV collapse ahead of monthly expiration forces underlying mean-reversion around high-open-interest nodes.",
                generation_source="template",
            )
        )

    # 3. Liquidity Clustered Pinning Momentum
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 1.1, group_neutralize(rank(ts_decay_linear(((close - forward_price_30) / (close * implied_volatility_mean_30 * sqrt(30 / 252.0) + 0.001)) * (pcr_vol_30 / (pcr_oi_30 + 0.001)), 15)), {grp}), -1)",
                archetype_name="Liquidity Clustered Strike Magnet",
                hypothesis="Disproportional options volume surges relative to open interest break pinning constraints into explosive directional moves.",
                generation_source="template",
            )
        )

    return candidates
