"""Formula templates for Institutional Order Flow Toxicity & VPIN."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_order_flow_vpin_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Volume-Synchronized Flow Toxicity Imbalance
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(((close - vwap) / (high - low + 0.001)) * (volume / adv20), 12)), {grp}), -1)",
                archetype_name="Volume Synchronized Flow Toxicity",
                hypothesis="Intraday VWAP divergence weighted by volume intensity reveals toxic informed institutional accumulation.",
                generation_source="template",
            )
        )

    # 2. Asymmetric Buy-Sell Volume Acceleration
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(ts_delta(volume / adv20, 5), 10)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(ts_delta(close, 3) * ts_zscore(volume, 20), 15)), {grp}), -1)",
                archetype_name="Asymmetric Order Flow Acceleration",
                hypothesis="Volume shocks aligned with directional price changes reflect institutional execution programs that persist over 15 days.",
                generation_source="template",
            )
        )

    # 3. PCR Flow Toxicity Confluence
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.7, group_neutralize(rank(ts_decay_linear(((close - open) / (high - low + 0.001)) * (1.0 / (pcr_vol_20 / (pcr_oi_20 + 0.001) + 0.01)), 15)), {grp}), -1)",
                archetype_name="Equity Flow vs Options Toxicity Confluence",
                hypothesis="Cash flow direction amplified by call volume dominance generates sustained multi-week excess returns.",
                generation_source="template",
            )
        )

    return candidates
