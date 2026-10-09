"""Model-Free Jump Variance & Risk-Neutral Moments Strategy Module."""
from __future__ import annotations

from brain_options.templates import OptionCandidate
from brain_options.strategies.base import BaseStrategy, StrategyMetadata
from brain_options.strategies.jump_variance_moments.fields import FIELDS
from brain_options.strategies.jump_variance_moments.templates import generate_jump_variance_moments_candidates


class JumpVarianceMomentsStrategy(BaseStrategy):
    """Exploits model-free jump variance curvature and higher-order risk-neutral moment dislocations."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id="jump_variance_moments",
            display_name="Model-Free Jump Variance & Risk-Neutral Moments",
            category="volatility_surface",
            theory_summary="Extracts discontinuous jump variance and tail kurtosis from option cross-sections, capturing non-linear risk compensation.",
            academic_references=[
                "Carr, P., & Madan, D. (2001). Towards a Theory of Volatility Trading. Cambridge University Press.",
                "Bollerslev, T., Tauchen, G., & Zhou, H. (2009). Expected Stock Returns and Variance Risk Premia. Review of Financial Studies.",
                "Bakshi, G., Kapadia, N., & Madan, D. (2003). Stock Return Characteristics, Option Prices, and Higher Moments. Review of Financial Studies.",
            ],
            preferred_universes=["TOP3000", "TOP2000", "TOP1000", "TOP500", "TOPSP500"],
            preferred_neutralizations=["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"],
            preferred_decays=[15, 20, 24],
        )

    def get_fields(self) -> list[str]:
        return list(FIELDS)

    def generate_candidates(self) -> list[OptionCandidate]:
        return generate_jump_variance_moments_candidates()
