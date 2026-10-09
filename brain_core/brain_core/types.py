"""
Shared, domain-agnostic data models used by all Brain libraries.

These are the single source of truth for field names and types.
All other libraries import from here. Never redefine these elsewhere.

Models
------
SimSettings    : immutable configuration for one BRAIN simulation run.
SimMetrics     : immutable result of one completed simulation.
AlphaCandidate : generic alpha expression descriptor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ── BRAIN simulation settings ─────────────────────────────────────────────

@dataclass(frozen=True)
class SimSettings:
    """
    Immutable configuration for a single WorldQuant BRAIN simulation.

    Field names and types match the BRAIN API payload; the camelCase
    conversion is handled inside to_simulation_payload().
    """
    region: str = "USA"
    universe: str = "TOP3000"
    delay: int = 1
    decay: int = 8
    neutralization: str = "SUBINDUSTRY"
    truncation: float = 0.05
    pasteurization: bool = True
    nan_handling: bool = False
    unit_handling: str = "VERIFY"
    language: str = "FASTEXPR"

    def to_simulation_payload(self, expression: str) -> dict[str, Any]:
        """Return a JSON-serialisable payload for the BRAIN /simulations endpoint."""
        return {
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": self.region,
                "universe": self.universe,
                "delay": self.delay,
                "decay": self.decay,
                "neutralization": self.neutralization.upper(),
                "truncation": self.truncation,
                "pasteurization": "ON" if self.pasteurization else "OFF",
                "unitHandling": self.unit_handling,
                "nanHandling": "ON" if self.nan_handling else "OFF",
                "language": self.language,
                "visualization": False,
            },
            "regular": expression,
        }


# ── BRAIN simulation results ──────────────────────────────────────────────

#: Status strings BRAIN returns when a simulation succeeded.
ACCEPTED_SIM_STATUSES: frozenset[str] = frozenset({"COMPLETE", "WARNING", "PASS", "SUCCESS"})


@dataclass(frozen=True)
class SimMetrics:
    """Immutable result payload from one completed BRAIN simulation."""
    alpha_id: Optional[str] = None
    sharpe: float = 0.0
    fitness: float = 0.0
    turnover: float = 0.0
    annualized_return: float = 0.0
    max_drawdown: float = 0.0
    margin: float = 0.0
    status: str = "ERROR"
    raw_response: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """
        True when the simulation completed successfully.

        Falls back to metric presence check for providers that
        omit or mislabel the status field but return real numbers.
        """
        if self.status.upper() in ACCEPTED_SIM_STATUSES:
            return True
        return self.sharpe != 0.0 or self.fitness != 0.0

    def passed_stage0(self, min_sharpe: float = 0.60, min_fitness: float = 0.50) -> bool:
        """True when this result clears Stage 0 Sharpe + Fitness gates."""
        return self.sharpe >= min_sharpe and self.fitness >= min_fitness


# ── Generic alpha candidate ───────────────────────────────────────────────

VALID_GENERATION_SOURCES: frozenset[str] = frozenset({
    "template",
    "llm",
    "llm_reasoning",
    "llm_mechanical",
    "procedural",
    "decorrelator",
    "synthesis",
    "sentiment",
    "risk_model",
    "options",
    "genetic",
    "manual",
})


@dataclass
class AlphaCandidate:
    """
    Generic, domain-agnostic alpha expression descriptor.

    Domain-specific libraries (brain_options, brain_sentiment,
    brain_risk_model) sub-class or compose this type to add their
    own fields.

    Fields
    ------
    expression        : The Fast Expression string to simulate.
    archetype_name    : Human-readable strategy archetype label.
    hypothesis        : One-sentence economic rationale for the signal.
    generation_source : One of 'template', 'llm', 'procedural', 'decorrelator', etc.
    base_alpha_id     : BRAIN alpha_id of the parent (decorrelation path only).
    operator_name     : Decorrelation axis, e.g. 'Axis 1 (Velocity Shift)'.
    """
    expression: str
    archetype_name: str
    hypothesis: str = ""
    generation_source: str = "template"
    base_alpha_id: Optional[str] = None
    operator_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.generation_source and self.generation_source not in VALID_GENERATION_SOURCES:
            raise ValueError(
                f"Invalid generation_source '{self.generation_source}'. "
                f"Must be one of: {sorted(VALID_GENERATION_SOURCES)}"
            )
