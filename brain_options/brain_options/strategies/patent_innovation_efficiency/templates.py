"""Formula templates for Patent Innovation Efficiency & R&D Dynamics."""
from __future__ import annotations
from brain_options.templates import OptionCandidate

def generate_patent_innovation_efficiency_candidates() -> list[OptionCandidate]:
    candidates: list[OptionCandidate] = []
    groups = ["subindustry"]

    # 1. Innovative Efficiency Ratio (Hirshleifer, Hsu, Li 2013, Cohen et al. 2013)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(patent_count / (ts_decay_linear(rd_expenditure, 252) + 1.0), 60)), {grp})",
                archetype_name="Innovative Efficiency Ratio",
                hypothesis="Firms generating high patent output relative to cumulative R&D investment possess superior intellectual property conversion.",
                generation_source="template",
            )
        )

    # 2. Patent Citation Velocity (Kogan et al. 2017)
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(ts_delta(patent_citations / (total_assets + 1.0), 40), 30)), {grp})",
                archetype_name="Patent Citation Velocity",
                hypothesis="Rapid acceleration in forward patent citations measures the economic impact of technological breakthroughs.",
                generation_source="template",
            )
        )

    # 3. High-Conviction R&D Intensity x Patent Output
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"trade_when(rd_expenditure > 0, group_neutralize(rank(ts_decay_linear((rd_expenditure / (sales + 1.0)) * (patent_count / (adv20 + 1.0)), 40)), {grp}), -1)",
                archetype_name="Conviction Gated Innovation Intensity",
                hypothesis="Focusing on active R&D spenders with high normalized patent grants isolates high-growth innovators.",
                generation_source="template",
            )
        )

    # 4. Citation-to-R&D Asset Spread
    for grp in groups:
        candidates.append(
            OptionCandidate(
                expression=f"group_neutralize(rank(ts_decay_linear(patent_citations / (total_assets + 1.0) - ts_decay_linear(rd_expenditure / (total_assets + 1.0), 126), 40)), {grp})",
                archetype_name="Citation-to-R&D Capital Spread",
                hypothesis="Firms where technological citations exceed historical R&D cost burdens deliver high risk-adjusted equity alpha.",
                generation_source="template",
            )
        )

    return candidates
