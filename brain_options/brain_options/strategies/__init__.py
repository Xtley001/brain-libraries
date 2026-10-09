"""
Modular Strategy Sub-System Registry for WorldQuant BRAIN Pipeline.
Provides auto-discovery, instantiation, and candidate aggregation across all 30 institutional quantitative strategy modules.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy

# 1-20 Institutional Strategies
from brain_options.strategies.term_structure import TermStructureStrategy
from brain_options.strategies.skew import SkewStrategy
from brain_options.strategies.pcr_flow import PCRFlowStrategy
from brain_options.strategies.breakeven import BreakevenStrategy
from brain_options.strategies.forward_basis import ForwardBasisStrategy
from brain_options.strategies.short_interest import ShortInterestStrategy
from brain_options.strategies.analyst_revisions import AnalystRevisionsStrategy
from brain_options.strategies.hybrid_confluence import HybridConfluenceStrategy
from brain_options.strategies.supply_chain import SupplyChainStrategy
from brain_options.strategies.accruals_cashflow import AccrualsCashflowStrategy
from brain_options.strategies.informed_short_demand import InformedShortDemandStrategy
from brain_options.strategies.extreme_tail_risk import ExtremeTailRiskStrategy
from brain_options.strategies.iv_lead_lag import IvLeadLagStrategy
from brain_options.strategies.network_momentum import NetworkMomentumStrategy
from brain_options.strategies.formulaic_101 import Formulaic101Strategy
from brain_options.strategies.institutional_13f_breadth import Institutional13fBreadthStrategy
from brain_options.strategies.insider_cluster_buying import InsiderClusterBuyingStrategy
from brain_options.strategies.peavd_earnings_vol_drift import PEAVDEarningsVolDriftStrategy
from brain_options.strategies.jump_variance_moments import JumpVarianceMomentsStrategy
from brain_options.strategies.patent_innovation_efficiency import PatentInnovationEfficiencyStrategy

# 21-30 Institutional Strategies (62+ Academic Papers & Books Expansion)
from brain_options.strategies.dynamic_short_squeeze import DynamicShortSqueezeStrategy
from brain_options.strategies.order_flow_vpin import OrderFlowVPINStrategy
from brain_options.strategies.gamma_pinning_clustering import GammaPinningClusteringStrategy
from brain_options.strategies.customer_supplier_cascades import CustomerSupplierCascadesStrategy
from brain_options.strategies.rd_capitalization_spillovers import RDCapitalizationSpilloversStrategy
from brain_options.strategies.capex_asset_growth import CapexAssetGrowthStrategy
from brain_options.strategies.peavrp_volatility_premia import PEAVRPVolatilityPremiaStrategy
from brain_options.strategies.realized_jump_intensity import RealizedJumpIntensityStrategy
from brain_options.strategies.distance_to_default_debt import DistanceToDefaultDebtStrategy
from brain_options.strategies.macro_fomc_cpi_drift import MacroFOMCCPIDriftStrategy

# Comprehensive Strategy Registry (30 Institutional Strategies)
STRATEGY_REGISTRY: dict[str, BaseStrategy] = {
    # 1-10 Core Volatility & Options
    "term_structure": TermStructureStrategy(),
    "skew": SkewStrategy(),
    "pcr_flow": PCRFlowStrategy(),
    "breakeven": BreakevenStrategy(),
    "forward_basis": ForwardBasisStrategy(),
    "extreme_tail_risk": ExtremeTailRiskStrategy(),
    "iv_lead_lag": IvLeadLagStrategy(),
    "peavd_earnings_vol_drift": PEAVDEarningsVolDriftStrategy(),
    "jump_variance_moments": JumpVarianceMomentsStrategy(),
    "gamma_pinning_clustering": GammaPinningClusteringStrategy(),
    # 11-20 Fundamental & Information Asymmetry
    "short_interest": ShortInterestStrategy(),
    "analyst_revisions": AnalystRevisionsStrategy(),
    "accruals_cashflow": AccrualsCashflowStrategy(),
    "informed_short_demand": InformedShortDemandStrategy(),
    "institutional_13f_breadth": Institutional13fBreadthStrategy(),
    "insider_cluster_buying": InsiderClusterBuyingStrategy(),
    "patent_innovation_efficiency": PatentInnovationEfficiencyStrategy(),
    "network_momentum": NetworkMomentumStrategy(),
    "supply_chain": SupplyChainStrategy(),
    "formulaic_101": Formulaic101Strategy(),
    # 21-30 Cross-Asset, Microstructure & Macro Premia
    "hybrid_confluence": HybridConfluenceStrategy(),
    "dynamic_short_squeeze": DynamicShortSqueezeStrategy(),
    "order_flow_vpin": OrderFlowVPINStrategy(),
    "customer_supplier_cascades": CustomerSupplierCascadesStrategy(),
    "rd_capitalization_spillovers": RDCapitalizationSpilloversStrategy(),
    "capex_asset_growth": CapexAssetGrowthStrategy(),
    "peavrp_volatility_premia": PEAVRPVolatilityPremiaStrategy(),
    "realized_jump_intensity": RealizedJumpIntensityStrategy(),
    "distance_to_default_debt": DistanceToDefaultDebtStrategy(),
    "macro_fomc_cpi_drift": MacroFOMCCPIDriftStrategy(),
}


def get_strategy(strategy_id: str) -> Optional[BaseStrategy]:
    """Retrieve a strategy instance by its identifier."""
    return STRATEGY_REGISTRY.get(strategy_id.lower().strip())


def list_strategy_ids() -> list[str]:
    """Returns all registered strategy IDs."""
    return list(STRATEGY_REGISTRY.keys())


def generate_modular_candidates(
    strategy_filter: Optional[str | list[str]] = None,
) -> list[OptionCandidate]:
    """
    Aggregates candidate expressions from the requested strategies.
    If strategy_filter is None or 'all', aggregates from all 30 strategies.
    """
    if strategy_filter is None or strategy_filter == "" or strategy_filter == "all":
        target_ids = list(STRATEGY_REGISTRY.keys())
    elif isinstance(strategy_filter, str):
        target_ids = [s.strip().lower() for s in strategy_filter.split(",") if s.strip()]
    else:
        target_ids = [s.strip().lower() for s in strategy_filter if s.strip()]

    candidates: list[OptionCandidate] = []
    for sid in target_ids:
        strat = STRATEGY_REGISTRY.get(sid)
        if strat:
            candidates.extend(strat.generate_candidates())

    return candidates
