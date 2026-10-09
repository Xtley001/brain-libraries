"""Templates for Network Graph Clustering & Co-Movement Lead-Lag Momentum."""
from __future__ import annotations

from brain_options.templates import OptionCandidate


def generate_network_momentum_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank(ts_decay_linear(returns, 20), {grp}) - group_rank(returns, {grp}), {grp})",
                archetype_name="Cluster Momentum Catch-Up",
                hypothesis="Stocks lagging the intermediate-term momentum of their peer cluster experience mean-reverting catch-up drift.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(returns - group_mean(returns, 20, {grp}), {grp}) * -1",
                archetype_name="Centroid Mean Reversion",
                hypothesis="Excess idiosyncratic return deviations from the industrial cluster centroid mean-revert over a 5-day horizon.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_regression_residuals(returns, group_mean(returns, 10, {grp}), 60)), {grp})",
                archetype_name="Residual Cluster Alpha",
                hypothesis="Orthogonalized residual returns net of sector cluster movements represent persistent pure alpha momentum.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank(ts_corr(returns, group_mean(returns, 20, {grp}), 60), {grp}) * group_rank(ts_decay_linear(returns, 10), {grp}), {grp})",
                archetype_name="Co-Movement Momentum Confluence",
                hypothesis="High central cluster co-movement interacting with strong recent momentum generates resilient cross-sectional alpha.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(-ts_zscore(returns - group_mean(returns * (cap / (group_mean(cap, {grp}) + 0.001)), {grp}), 10)), {grp})",
                archetype_name="Cap-Weighted Centroid Reversion",
                hypothesis="Large-cap weighted cluster centroids provide higher-fidelity lead signals than equal-weighted centroids.",
                generation_source="template",
            )
        )

    return candidates
