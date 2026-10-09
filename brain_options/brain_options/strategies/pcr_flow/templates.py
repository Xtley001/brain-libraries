"""Formula templates for Put-Call Ratio & Order Flow."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_pcr_flow_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Put-Call Ratio Contrarian Reversal
    for tenor in [10, 20, 30]:
        for window in [10, 20]:
            for grp in groups:
                candidates.append(
                    OptionCandidate(
                        expression=f"group_neutralize(rank(-ts_zscore(pcr_vol_{tenor}, {window})), {grp})",
                        archetype_name="Put-Call Ratio Contrarian Reversal",
                        hypothesis=f"Extreme spikes in {tenor}d put volume indicate capitulation and oversold bounce opportunity.",
                        generation_source="template",
                    )
                )

    # 2. PCR Volume-to-OI Flow Surge
    for tenor in [10, 20, 30]:
        for window in [10, 20]:
            for grp in groups:
                candidates.append(
                    OptionCandidate(
                        expression=f"group_neutralize(rank(-ts_rank(pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001), {window})), {grp})",
                        archetype_name="PCR Volume-to-OI Flow Surge",
                        hypothesis=f"Surge in {tenor}d put volume relative to open interest stock identifies active smart money hedging.",
                        generation_source="template",
                    )
                )

    # 3. Pan-Poteshman Informed Option Flow (Liquidity gated & linear decayed)
    for tenor in [10, 20, 30]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(volume > adv20, group_neutralize(rank(-ts_decay_linear(pcr_vol_{tenor} / (pcr_oi_{tenor} + 0.001), 5)), {grp}), -1)",
                    archetype_name="Pan-Poteshman Informed Option Flow",
                    hypothesis=f"Pan & Poteshman (2006): Opening put volume surges confirmed by underlying liquidity lead prices by 1-2 days.",
                    generation_source="template",
                )
            )

    # 4. Open Interest Buildup Contrarian Positioning
    for tenor in [20, 30]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-ts_decay_linear(ts_delta(pcr_oi_{tenor}, 10), 5)), {grp})",
                    archetype_name="Put Open Interest Buildup",
                    hypothesis=f"Accumulation of put open interest at {tenor}d tenor captures structural options overhang.",
                    generation_source="template",
                )
            )

    # 5. Slow Flow-Regime Baseline Companion & Strict Liquidity Gating
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20, group_neutralize(rank(-ts_decay_linear(pcr_vol_10 / (pcr_oi_10 + 0.001) - pcr_vol_60 / (pcr_oi_60 + 0.001), 5)), {grp}), -1)",
                archetype_name="Flow Regime Baseline Spread",
                hypothesis="Nets out short-term volume-to-OI surge relative to 60-day baseline to isolate signed institutional order flow.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > 1.5 * adv20, group_neutralize(rank(-ts_decay_linear(pcr_vol_20 / (pcr_oi_20 + 0.001), 5)), {grp}), -1)",
                archetype_name="Strict Liquidity Gated Flow",
                hypothesis="1.5x ADV20 volume confirmation ensures flow surges reflect true high-conviction order flow.",
                generation_source="template",
            )
        )

    return candidates
