"""Formula templates for Dynamic Short Squeeze & Borrow Fee Convexity."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_dynamic_short_squeeze_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Borrow Fee Acceleration x High Short Interest Squeeze
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_delta(borrow_fee, 5) * (short_interest / (shares_out + 1.0)), 12)), {grp}), -1)",
                archetype_name="Borrow Fee Acceleration Squeeze",
                hypothesis="Rapid acceleration in equity borrow fees coupled with high short float creates mandatory short recall squeezes.",
                generation_source="template",
            )
        )

    # 2. Skew Smirk x Utilization Inelasticity
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(ts_zscore(borrow_fee, 60), 15)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(ts_zscore(borrow_fee, 60) * (implied_volatility_mean_skew_30 * sqrt(30 / 252.0)), 15)), {grp}), -1)",
                archetype_name="Borrow Inelasticity Put Skew Confluence",
                hypothesis="Extreme equity borrow rates interact with put skew smirks to identify unsustainable downside crowding.",
                generation_source="template",
            )
        )

    # 3. Short Cover Volume Surge Momentum
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 1.2, group_neutralize(rank(ts_decay_linear(ts_delta(close, 3) * (borrow_fee / (ts_mean(borrow_fee, 20) + 0.01)), 10)), {grp}), -1)",
                archetype_name="Short Cover Volume Surge",
                hypothesis="Volume spikes on highly borrowed stocks trigger violent multi-day positive price runs as shorts buy to close.",
                generation_source="template",
            )
        )

    return candidates
