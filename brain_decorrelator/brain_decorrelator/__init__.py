"""
brain_decorrelator — strategy-agnostic alpha decorrelation engine.

Public API
----------
DecorrelationEngine   : Main engine. Call generate_orthogonal_variants().
DecorrelationResult   : Named tuple holding one variant + metadata.
AxisPlugin            : Abstract base class for axis plugins.
register_axis         : Decorator to register a custom axis plugin.
"""
from brain_decorrelator.engine import DecorrelationEngine, DecorrelationResult
from brain_decorrelator.plugin import (
    AxisPlugin,
    register_axis,
    unregister_axis,
    get_registered_axes,
)
import brain_decorrelator.axes.universal  # Register default universal axes

__all__ = [
    "DecorrelationEngine",
    "DecorrelationResult",
    "AxisPlugin",
    "register_axis",
    "unregister_axis",
    "get_registered_axes",
]
