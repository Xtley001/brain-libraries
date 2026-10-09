"""Formula templates for Customer-Supplier Revenue Concentration & Cascades."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_customer_supplier_cascades_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Customer Sector Lead-Lag Diffusion
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_delay(group_mean(returns, 20, {grp}), 5) - returns, 15)), {grp}), -1)",
                archetype_name="Customer Sector Return Diffusion",
                hypothesis="Economic linkages across supply chains cause downstream customer momentum to diffuse into suppliers with a 5-20 day lag.",
                generation_source="template",
            )
        )

    # 2. Inventory Accumulation Bottleneck Divergence
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(abs(rank(ts_decay_linear(ts_delta(inventory / (sales + 1.0), 60), 20)) - 0.5) > 0.35, group_neutralize(rank(ts_decay_linear(-ts_delta(inventory / (cogs + 1.0), 60), 20)), {grp}), -1)",
                archetype_name="Inventory Bottleneck Propagation",
                hypothesis="Bloated inventory relative to cost of goods sold flags customer order cancellations and supplier gross margin compression.",
                generation_source="template",
            )
        )

    # 3. Supply Chain Margin Compression Shock
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.7, group_neutralize(rank(ts_decay_linear(ts_delta((sales - cogs) / (sales + 1.0), 60) * (1.0 / (implied_volatility_mean_30 + 0.01)), 20)), {grp}), -1)",
                archetype_name="Supply Chain Gross Margin Expansion",
                hypothesis="Suppliers demonstrating expanding gross margins conditioned by low volatility surprise markets on consecutive earnings.",
                generation_source="template",
            )
        )

    return candidates
