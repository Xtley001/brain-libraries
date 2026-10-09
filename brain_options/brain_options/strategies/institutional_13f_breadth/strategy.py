"""Institutional 13F Ownership Breadth & Smart Money Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.institutional_13f_breadth.fields import FIELDS
from brain_options.strategies.institutional_13f_breadth.templates import generate_institutional_13f_breadth_candidates


class Institutional13fBreadthStrategy(BaseStrategy):
    """Exploits changes in breadth and concentration of institutional 13F ownership."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="institutional_13f_breadth",
            display_name="Institutional 13F Ownership Breadth & Smart-Money Dynamics",
            category="institutional_flow",
            theory_summary="Measures expansion in the number of unique institutional owners to detect early smart-money consensus before broad price discovery.",
            academic_references=[
                "Chen, J., Hong, H., & Stein, J.C. (2002). Breadth of Ownership and Stock Returns. Journal of Financial Economics.",
                "Sias, R.W., Starks, L.T., & Titman, S. (2006). Changes in Institutional Ownership and Stock Returns: Assessment and Methodology. Journal of Business.",
                "Grinold, R., & Kahn, R. (1999). Active Portfolio Management. McGraw-Hill.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[15, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_institutional_13f_breadth_candidates()
