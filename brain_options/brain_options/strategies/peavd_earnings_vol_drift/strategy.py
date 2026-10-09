"""Post-Earnings Announcement Volatility Drift (PEAVD) Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.peavd_earnings_vol_drift.fields import FIELDS
from brain_options.strategies.peavd_earnings_vol_drift.templates import generate_peavd_earnings_vol_drift_candidates


class PEAVDEarningsVolDriftStrategy(BaseStrategy):
    """Exploits Post-Earnings Announcement Drift (PEAD) conditioned on options IV term structure."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="peavd_earnings_vol_drift",
            display_name="Post-Earnings Announcement Volatility Drift (PEAVD)",
            category="earnings_drift",
            theory_summary="Captures systematic price under-reaction following earnings surprises, scaled by option implied volatility term structure dynamics.",
            academic_references=[
                "Ball, R., & Brown, P. (1968). An Empirical Evaluation of Accounting Income Numbers. Journal of Accounting Research.",
                "Bernard, V.L., & Thomas, J.K. (1989). Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium? Journal of Accounting and Economics.",
                "Patel, J.M., & Wolfson, M.A. (1984). The Ex-Ante and Ex-Post Price Effects of Quarterly Earnings Announcements.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[15, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_peavd_earnings_vol_drift_candidates()
