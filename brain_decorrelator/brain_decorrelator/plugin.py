"""
Plugin architecture for decorrelation axes.

Each axis is an AxisPlugin subclass registered with @register_axis.
The DecorrelationEngine calls every registered plugin in order and
collects the non-empty variants each returns.

Domain libraries (brain_options, brain_sentiment, etc.) may register
domain-specific plugins without modifying this package:

    from brain_decorrelator import register_axis, AxisPlugin

    @register_axis
    class OptionsMoneynessMirror(AxisPlugin):
        name = "Axis 9 (Moneyness Inversion)"

        def apply(self, expr: str, context: dict) -> list[str]:
            ...
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import ClassVar, List

log = logging.getLogger("brain_decorrelator.plugin")

# Global plugin registry — populated by @register_axis
_AXIS_REGISTRY: list["AxisPlugin"] = []


class AxisPlugin(ABC):
    """Abstract base class for a decorrelation axis."""

    #: Unique human-readable axis name, e.g. "Axis 1 (Velocity Shift)".
    name: ClassVar[str] = "Unnamed Axis"

    @abstractmethod
    def apply(self, expr: str, context: dict) -> List[str]:
        """
        Generate orthogonal variants of *expr*.

        Parameters
        ----------
        expr    : The base Fast Expression string to decorrelate.
        context : Arbitrary metadata dict supplied by the caller.
                  Standard keys (all optional):
                    "archetype"         str  — archetype label
                    "base_sharpe"       float
                    "colliding_id"      str  — BRAIN alpha_id of the colliding alpha
                    "colliding_factor"  str  — factor type of the collider
                    "dedup_hashes"      set  — already-seen expression hashes

        Returns
        -------
        List of orthogonal expression strings (may be empty).
        """

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AxisPlugin name={self.name!r}>"


def register_axis(cls: type) -> type:
    """
    Class decorator that adds an instance of *cls* to the global axis registry.

    Usage::

        @register_axis
        class MyAxis(AxisPlugin):
            name = "Axis X (My Transform)"
            def apply(self, expr, context): ...
    """
    instance = cls()
    _AXIS_REGISTRY.append(instance)
    log.debug("brain_decorrelator: Registered axis %r", cls.name)
    return cls


def get_registered_axes() -> list[AxisPlugin]:
    """Return a shallow copy of the current axis registry."""
    return list(_AXIS_REGISTRY)


def unregister_axis(plugin_or_cls: AxisPlugin | type) -> None:
    """
    Remove an axis from the registry. Primarily for test isolation.
    Accepts either an AxisPlugin instance or an AxisPlugin subclass.
    """
    global _AXIS_REGISTRY
    if isinstance(plugin_or_cls, type):
        _AXIS_REGISTRY = [a for a in _AXIS_REGISTRY if not isinstance(a, plugin_or_cls)]
    else:
        _AXIS_REGISTRY = [a for a in _AXIS_REGISTRY if a is not plugin_or_cls]
