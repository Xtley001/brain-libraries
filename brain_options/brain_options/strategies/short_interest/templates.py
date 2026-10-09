"""Formula templates for Short Interest & Borrow Pressure."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_short_interest_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Institutional Borrow Fee Surge x Short Scale
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_decay_linear(borrow_fee * (short_interest / (float_shares + 0.001)), 20)), {grp})",
                archetype_name="Short Demand Borrow Surge",
                hypothesis="Cohen et al. (2007): Inward shifts in short supply coupled with high borrowing demand isolate high-conviction shorting.",
                generation_source="template",
            )
        )

    # 2. De-Trended Short Interest Z-Score
    for window in [126, 252]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear(ts_zscore(short_interest / (float_shares + 0.001), {window}), 20)), {grp})",
                    archetype_name="De-Trended Short Interest Z-Score",
                    hypothesis=f"Rapach et al. (2016): De-trended {window}d short interest Z-score measures abnormal institutional bearish positioning.",
                    generation_source="template",
                )
            )

    # 3. Days-to-Cover Short Squeeze Breakout
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when((close > ts_mean(close, 20)) & (days_to_cover > 5.0), group_neutralize(rank(ts_decay_linear(days_to_cover * ts_delta(close, 5), 15)), {grp}), -1)",
                archetype_name="Days-to-Cover Short Squeeze Breakout",
                hypothesis="Asquith et al. (2005): Heavy days-to-cover positions face forced margin buy-ins upon upward price breakouts.",
                generation_source="template",
            )
        )

    # 4. Short Interest Velocity Acceleration
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_delta(short_interest / (float_shares + 0.001), 10)), {grp})",
                archetype_name="Short Interest Velocity",
                hypothesis="Rapidly accelerating short interest accumulation reveals private negative information.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_zscore(volume / adv20, 10) * rank(short_interest / (float_shares + 1.0))), {grp})",
                archetype_name="Volume Squeeze Forced Covering",
                hypothesis="Sudden volume surge in heavily shorted equities indicates forced buy-ins and short covering rallies.",
                generation_source="template",
            )
        )

    return candidates
