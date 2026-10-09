"""Formula templates for Institutional 13F Ownership Breadth & Smart-Money Dynamics."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_institutional_13f_breadth_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Breadth of Ownership Delta (Chen, Hong, Stein 2002)
    for window in [30, 60, 90]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((inst_owners_count - ts_delay(inst_owners_count, {window})) / (ts_delay(inst_owners_count, {window}) + 1.0), 20)), {grp})",
                    archetype_name="Institutional Ownership Breadth Delta",
                    hypothesis=f"Growth in the number of unique institutional holders over {window}d predicts multi-month upward drift.",
                    generation_source="template",
                )
            )

    # 2. High-Conviction Gated Institutional Breadth Expansion
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear((inst_owners_count - ts_delay(inst_owners_count, 60)) / (ts_delay(inst_owners_count, 60) + 1.0), 20)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear((inst_owners_count - ts_delay(inst_owners_count, 60)) / (ts_delay(inst_owners_count, 60) + 1.0), 20)), {grp}), -1)",
                archetype_name="Conviction Gated Institutional Breadth",
                hypothesis="High-conviction tail changes in institutional ownership breadth eliminate noise and lower portfolio turnover.",
                generation_source="template",
            )
        )

    # 3. Institutional Holding Shares Acceleration (Sias et al. 2006)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_delta(inst_holding_shares / (adv20 + 1.0), 10), 15)), {grp})",
                archetype_name="Institutional Holding Shares Acceleration",
                hypothesis="Acceleration in shares held by institutions normalized by trading volume captures aggressive smart-money accumulation.",
                generation_source="template",
            )
        )

    # 4. Institutional Breadth vs Holdings Asymmetry
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_zscore(inst_owners_count, 60) - ts_zscore(inst_holding_shares, 60), 20)), {grp})",
                archetype_name="Institutional Breadth-Holdings Asymmetry",
                hypothesis="When the number of unique institutional owners expands faster than raw share count, broad-based adoption reduces concentration risk.",
                generation_source="template",
            )
        )

    # 5. Institutional Ownership Percentage Velocity
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_delta(inst_holding_pct, 20), 20)), {grp})",
                archetype_name="Institutional Ownership Percentage Velocity",
                hypothesis="Quarter-over-quarter upward shifts in total institutional equity percentage signal structural fund inflows.",
                generation_source="template",
            )
        )

    return candidates
