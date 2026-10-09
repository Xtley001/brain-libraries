"""Formula templates for R&D Capitalization & Technology Spillovers."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_rd_capitalization_spillovers_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. R&D Capital Intensity relative to Assets
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_mean(rd_expense / (total_assets + 1.0), 60), 20)), {grp}), -1)",
                archetype_name="R&D Asset Capitalization Intensity",
                hypothesis="Firms investing heavily in R&D relative to total assets build intangible capital and pricing power that markets persistently under-react to.",
                generation_source="template",
            )
        )

    # 2. R&D Efficiency Growth Shock
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear(ts_delta(sales / (rd_expense + 1.0), 60) * (1.0 / (implied_volatility_mean_30 + 0.01)), 15)), {grp}), -1)",
                archetype_name="R&D Revenue Conversion Efficiency",
                hypothesis="High conversion rate of R&D expenditure into top-line sales paired with low option implied volatility forecasts persistent drift.",
                generation_source="template",
            )
        )

    # 3. Technology Spillover Momentum Divergence
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(volume > adv20 * 0.8, group_neutralize(rank(ts_decay_linear((rd_expense / (sales + 1.0)) - group_mean(rd_expense / (sales + 1.0), 20, {grp}), 18)), {grp}), -1)",
                archetype_name="Sector R&D Leadership Spillover",
                hypothesis="Intra-industry R&D leaders generate positive knowledge spillovers that widen competitive moats over sector peers.",
                generation_source="template",
            )
        )

    return candidates
