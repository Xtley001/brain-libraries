"""Cross-Asset Implied Volatility Leading Cash Equity Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.iv_lead_lag.fields import FIELDS
from brain_options.strategies.iv_lead_lag.templates import generate_iv_lead_lag_candidates


class IvLeadLagStrategy(BaseStrategy):
    """Exploits information discovery in the options market leading forward cash equity prices."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="iv_lead_lag",
            display_name="Cross-Asset Implied Volatility Leading Cash Equity",
            category="cross_asset_lead_lag",
            theory_summary="Extracts informed directional signals from options implied volatility dynamics and volume imbalances preceding equity drift.",
            academic_references=[
                "Bali, T.G., & Hovakimian, A. (2009). Volatility Spreads and Expected Stock Returns. Management Science.",
                "Pan, J., & Poteshman, A.M. (2006). The Information in Option Volume for Future Stock Prices. Review of Financial Studies.",
                "Garleanu, N., & Pedersen, L.H. (2011). Margin Requirements and Asset Prices.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[8, 10, 12],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_iv_lead_lag_candidates()
