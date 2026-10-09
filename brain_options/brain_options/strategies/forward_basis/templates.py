"""Formula templates for Synthetic Forward Basis strategies."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_forward_basis_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Forward Basis Spread across tenors with linear decay smoothing (window=15)
    for tenor in [10, 20, 30, 60, 90]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(ts_decay_linear((forward_price_{tenor} - close) / close, 15)), {grp})",
                    archetype_name="Forward Basis Spread",
                    hypothesis=f"Synthetic forward basis at {tenor}d tenor smoothed with 15d decay demeaned by {grp} predicts drift.",
                    generation_source="template",
                )
            )

    # 2. High-Conviction Gated Forward Basis (threshold 0.35, holds top/bottom 15% names)
    for tenor in [30, 60, 90]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(abs(rank(ts_decay_linear((forward_price_{tenor} - close) / close, 15)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear((forward_price_{tenor} - close) / close, 15)), {grp}), -1)",
                    archetype_name="Forward Basis Conviction Spread",
                    hypothesis=f"High-conviction tail positions on {tenor}d synthetic forward basis drop turnover and boost Fitness.",
                    generation_source="template",
                )
            )

    # 3. Forward Basis Velocity with Decay
    for tenor in [20, 30, 60]:
        for window in [5, 10]:
            for grp in groups:
                candidates.append(
                    OptionCandidate(
                        expression=f"group_neutralize(rank(ts_decay_linear(ts_delta((forward_price_{tenor} - close) / close, {window}), 10)), {grp})",
                        archetype_name="Forward Basis Velocity",
                        hypothesis=f"Smoothed rate of change in {tenor}d forward basis over {window}d window identifies accumulation.",
                        generation_source="template",
                    )
                )

    # 4. Decayed Forward Basis Acceleration with Conviction Gate
    for tenor in [30, 60]:
        for grp in groups:
            candidates.append(
                OptionCandidate(
                    expression=f"trade_when(abs(rank(ts_decay_linear(ts_delta((forward_price_{tenor} - close) / close, 5), 10)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(ts_delta((forward_price_{tenor} - close) / close, 5), 10)), {grp}), -1)",
                    archetype_name="Decayed Forward Basis Acceleration",
                    hypothesis="Conviction-gated smoothed acceleration in forward basis isolates sustained institutional position shifts.",
                    generation_source="template",
                )
            )

    # 5. Forward Basis Term Structure Slope (30d vs 90d)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear((forward_price_30 - close) / close - (forward_price_90 - close) / close, 15)), {grp})",
                archetype_name="Forward Basis Term Structure",
                hypothesis="Comparing 30d to 90d forward basis with 15d linear decay captures term structure divergence in carrying cost.",
                generation_source="template",
            )
        )

    return candidates
