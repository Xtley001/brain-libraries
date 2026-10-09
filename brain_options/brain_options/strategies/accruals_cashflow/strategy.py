"""Accounting Quality & Sloan Accruals Anomaly Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.accruals_cashflow.fields import FIELDS
from brain_options.strategies.accruals_cashflow.templates import generate_accruals_cashflow_candidates


class AccrualsCashflowStrategy(BaseStrategy):
    """Exploits divergence between reported accounting earnings and underlying operating cash flows."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="accruals_cashflow",
            display_name="Accounting Quality, Sloan Cash Flow Divergence & Accruals Anomaly",
            category="fundamental_quality",
            theory_summary="Identifies earnings persistence mispricings: firms with high cash-backed earnings outperform aggressive accrual estimators.",
            academic_references=[
                "Sloan, R.G. (1996). Do Stock Prices Fully Reflect Information in Accruals and Cash Flows about Future Earnings? The Accounting Review.",
                "Fabozzi, F.J. (2007). Quantitative Equity Investing. John Wiley & Sons.",
                "Grinold, R., & Kahn, R. (1999). Active Portfolio Management. McGraw-Hill.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[15, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_accruals_cashflow_candidates()
