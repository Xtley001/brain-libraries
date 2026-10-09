"""Patent Innovation Efficiency Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.patent_innovation_efficiency.fields import FIELDS
from brain_options.strategies.patent_innovation_efficiency.templates import generate_patent_innovation_efficiency_candidates


class PatentInnovationEfficiencyStrategy(BaseStrategy):
    """Exploits technological innovation, patent citation velocity, and R&D conversion efficiency."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="patent_innovation_efficiency",
            display_name="Patent Innovation Efficiency & R&D Network Momentum",
            category="intangible_capital",
            theory_summary="Measures firm-level innovative efficiency by scaling patent counts and citation impact against cumulative R&D investment.",
            academic_references=[
                "Cohen, L., Diether, K., & Malloy, C. (2013). Misvaluing Innovation. Review of Financial Studies.",
                "Kogan, L., Papanikolaou, D., Seru, A., & Stoffman, N. (2017). Technological Innovation, Resource Allocation, and Growth. Quarterly Journal of Economics.",
                "Hirshleifer, D., Hsu, P.H., & Li, D. (2013). Innovative Efficiency and Stock Returns. Journal of Financial Economics.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["INDUSTRY", "SUBINDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[20, 30, 40],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_patent_innovation_efficiency_candidates()
