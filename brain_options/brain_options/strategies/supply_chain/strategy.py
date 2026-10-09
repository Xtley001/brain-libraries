"""Supply Chain Shock Propagation & Customer-Supplier Lead-Lag Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.supply_chain.fields import FIELDS
from brain_options.strategies.supply_chain.templates import generate_supply_chain_candidates


class SupplyChainStrategy(BaseStrategy):
    """Exploits information transmission delays and economic shock propagation across supplier-customer networks."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="supply_chain",
            display_name="Supply Chain Shock Propagation & Customer-Supplier Lead-Lag",
            category="network_macro",
            theory_summary="Captures lagged cash-flow and demand transmission through industrial production networks and customer-supplier links.",
            academic_references=[
                "Barrot, J.N., & Sauvagnat, J. (2016). Input Specificity and the Propagation of Idiosyncratic Shocks in Production Networks. Quarterly Journal of Economics.",
                "Cohen, L., & Frazzini, A. (2008). Economic Links and Predictable Returns. Journal of Finance.",
                "Menzies et al. (2020). Economically Linked Firms and Cross-Industry Lead-Lag Predictability.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET", "NONE"],
            preferred_decays=[8, 10, 15],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_supply_chain_candidates()
