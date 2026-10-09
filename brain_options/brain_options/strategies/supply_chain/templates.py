"""Templates for Supply Chain Shock Propagation & Customer-Supplier Lead-Lag."""
from __future__ import annotations

from brain_options.templates import OptionCandidate


def generate_supply_chain_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(ts_delay(group_mean(returns, 20, {grp}), 5) - returns, {grp})",
                archetype_name="Supply Chain Lead-Lag Momentum",
                hypothesis=f"Upstream supplier return shocks diffuse with a 5-day lag to customer firms within {grp}.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(group_rank(ts_delay(group_mean(eps_surprise, 60, {grp}), 10), {grp}) - group_rank(returns, {grp}), {grp})",
                archetype_name="Supply Chain Earnings Diffusion",
                hypothesis=f"Supplier sector earnings surprise drift creates predictable cross-industry lead-lag return momentum in {grp}.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(inventory_turnover - ts_delay(inventory_turnover, 20), 10)) * -1, {grp})",
                archetype_name="Supply Chain Inventory Bottleneck",
                hypothesis=f"Inventory accumulation bottlenecks signal order cancellations across customer production lines.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(ts_regression_residuals(returns, ts_delay(group_mean(returns, 10, {grp}), 3), 20), {grp})",
                archetype_name="Supply Chain Residual Momentum",
                hypothesis=f"Residual returns after orthogonalizing against delayed industrial peer returns isolate idiosyncratic firm momentum.",
                generation_source="template",
            )
        )
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_delay(group_mean(-ts_delta(cogs / (sales + 1.0), 20), {grp}), 10)), industry)",
                archetype_name="COGS Cost-Pressure Propagation",
                hypothesis="Rising COGS/sales in supplier clusters propagates forward to customer margins independent of earnings calendar clustering.",
                generation_source="template",
            )
        )

    return candidates
