"""Formula templates for Term Structure and Variance Risk Premium."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_term_structure_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Volatility Term Structure Slope / Inversion (Front vs 3-month)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(implied_volatility_mean_30 / (implied_volatility_mean_90 + 0.001) - 1.0)), {grp})",
                archetype_name="Volatility Term Structure Slope",
                hypothesis="Front-month IV exceeding 3-month IV signals temporary panic pricing that mean-reverts.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(-(implied_volatility_mean_20 / (implied_volatility_mean_60 + 0.001) - 1.0), 10)), {grp})",
                archetype_name="Smoothed Term Structure Inversion",
                hypothesis="Linear decayed 20d/60d term structure inversion filters high-frequency noise.",
                generation_source="template",
            )
        )

    # 2. Variance Risk Premium (VRP: IV - Realized Vol)
    for tenor, window in [(20, 20), (30, 30)]:
        for grp in ["subindustry", "industry"]:
            candidates.append(
                OptionCandidate(
                    expression=f"group_neutralize(rank(-(implied_volatility_mean_{tenor} - ts_std_dev(returns, {window}) * 15.87)), {grp})",
                    archetype_name="Variance Risk Premium",
                    hypothesis=f"Structural variance risk premium: {tenor}d IV exceeding {window}d RV predicts future underperformance drag.",
                    generation_source="template",
                )
            )

    # 3. Jensen-Debiased Variance Risk Premium (16.53 multiplier)
    for grp in ["subindustry", "sector"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(implied_volatility_mean_30 - ts_std_dev(returns, 30) * 16.53)), {grp})",
                archetype_name="Jensen-Debiased Variance Risk Premium",
                hypothesis="Realized volatility estimator downward bias corrected by 16.53 multiplier eliminates false-positive VRP richness.",
                generation_source="template",
            )
        )

    # 4. Sinclair Optimal Mean-Reversion Gated Entry (~0.75 SD)
    for grp in ["subindustry", "sector"]:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(ts_zscore(implied_volatility_mean_30 - ts_std_dev(returns, 30) * 15.87, 40)) > 0.75, group_neutralize(rank(-(implied_volatility_mean_30 - ts_std_dev(returns, 30) * 15.87)), {grp}), -1)",
                archetype_name="Optimal Gated VRP",
                hypothesis="Entering VRP when standardized deviation exceeds 0.75 SD maximizes compound growth.",
                generation_source="template",
            )
        )

    # 5. Carr-Wu Quadratic Variance Risk Premium
    for grp in ["subindustry", "industry"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(signed_power(implied_volatility_mean_30, 2) - signed_power(ts_std_dev(returns, 20), 2) * 252)), {grp})",
                archetype_name="Carr-Wu Quadratic VRP",
                hypothesis="Variance swap synthetic replication demonstrates VRP is quadratic in IV.",
                generation_source="template",
            )
        )

    # 6. Pairwise Forward Volatility Term Notch
    for grp in ["subindustry", "sector"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(sqrt(max(0.0001, (signed_power(implied_volatility_mean_90, 2) * 90 - signed_power(implied_volatility_mean_30, 2) * 30) / 60)) - implied_volatility_mean_30)), {grp})",
                archetype_name="Pairwise Forward Vol Notch",
                hypothesis="Forward volatility extracted across tenors isolates catalyst event risk.",
                generation_source="template",
            )
        )

    # 7. VRP Velocity (Rolling Acceleration)
    for grp in ["subindustry", "industry"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_delta(-(implied_volatility_mean_30 - ts_std_dev(returns, 30) * 15.87), 5)), {grp})",
                archetype_name="VRP Velocity",
                hypothesis="VRP velocity captures rapid variance risk premium acceleration before consensus recognizes mean-reversion.",
                generation_source="template",
            )
        )

    # 8. Long-Tenor 30d/180d Vol Term Structure Slope
    for grp in ["subindustry", "sector"]:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-(implied_volatility_mean_30 / (implied_volatility_mean_180 + 0.001) - 1.0)), {grp})",
                archetype_name="Long Tenor Term Slope",
                hypothesis="Comparing 30d to 180d IV provides structural long-horizon volatility risk premium read.",
                generation_source="template",
            )
        )

    return candidates
