"""Synthetic Forward Basis Quantitative Strategy Module."""
from __future__ import annotations

from typing import List, Optional
from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.forward_basis.fields import FIELDS
from brain_options.strategies.forward_basis.templates import generate_forward_basis_candidates


class ForwardBasisStrategy(BaseStrategy):
    """Exploits synthetic forward prices derived from put-call parity deviations and carrying cost drift."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="forward_basis",
            display_name="Synthetic Forward Basis Spread",
            category="parity_arbitrage",
            theory_summary="Quantifies divergence between options-implied synthetic forward prices and cash equity prices.",
            academic_references=[
                "Cremers, M., & Weinbaum, D. (2010). Deviations from Put-Call Parity and Stock Returns. JFQA.",
                "Ofek, E., Richardson, M., & Whitelaw, R. F. (2004). Limited Arbitrage and Short Sales Restrictions. JFE.",
            ],
            preferred_universes=["TOP2000", "TOP1000", "TOP3000"],
            preferred_neutralizations=["SUBINDUSTRY", "SECTOR", "INDUSTRY", "MARKET"],
            preferred_decays=[18, 22, 26],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_forward_basis_candidates()
