"""Strategy module for Customer-Supplier Revenue Concentration & Cascades."""
from __future__ import annotations

from typing import Any, List
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.customer_supplier_cascades.fields import FIELDS
from brain_options.strategies.customer_supplier_cascades.templates import generate_customer_supplier_cascades_candidates


class CustomerSupplierCascadesStrategy(BaseStrategy):
    """Exploits inter-firm supply chain network shocks, inventory bottlenecks, and revenue concentration diffusion."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="customer_supplier_cascades",
            display_name="Customer-Supplier Revenue Concentration & Cascades",
            category="fundamental",
            theory_summary="Isolates supply chain information lags where customer demand shocks diffuse into supplier revenues and margins.",
            academic_references=[
                "Fee, Thomas (2004): Sources of Gains in Horizontal Mergers: Evidence from Customer, Supplier, and Rival Firms",
                "Menzly, Ozbas (2010): Market Segmentation and Cross-Predictability of Returns",
                "Barrot, Sauvagnat (2016): Input Specificity and the Propagation of Idiosyncratic Shocks",
            ],
            preferred_universes=["TOP1000", "TOP2000", "TOP3000", "TOP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR"],
            preferred_decays=[14, 16, 20],
        )

    def get_fields(self) -> List[str]:
        return list(FIELDS)

    def generate_candidates(self) -> List[OptionCandidate]:
        return generate_customer_supplier_cascades_candidates()
