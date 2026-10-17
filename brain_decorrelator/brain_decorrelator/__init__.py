"""
brain_decorrelator — strategy-agnostic alpha decorrelation engine.

Public API (v0.2.0)
-------------------
DecorrelationEngine   : Main engine. Call generate_orthogonal_variants().
DecorrelationResult   : Named tuple holding one variant + metadata.
AxisPlugin            : Abstract base class for axis plugins.
register_axis         : Decorator to register a custom axis plugin.
unregister_axis       : Remove axis from registry.
get_registered_axes   : Return registered axes.
parse_ast             : Parse Fast Expression into AST.
unparse_ast           : Serialize AST back to expression.
ASTNode               : AST node dataclass.
VetoMemory            : AlphaMemo asymmetric veto memory store.
CollisionRecord       : Record of correlation gate collision.
"""
from brain_decorrelator.engine import DecorrelationEngine, DecorrelationResult
from brain_decorrelator.plugin import (
    AxisPlugin,
    register_axis,
    unregister_axis,
    get_registered_axes,
)
from brain_decorrelator.ast_engine.parser import ASTNode, parse_ast, unparse_ast
from brain_decorrelator.veto_memory.store import VetoMemory, CollisionRecord
import brain_decorrelator.axes  # Auto-registers universal and new academic axes

__all__ = [
    "DecorrelationEngine",
    "DecorrelationResult",
    "AxisPlugin",
    "register_axis",
    "unregister_axis",
    "get_registered_axes",
    "ASTNode",
    "parse_ast",
    "unparse_ast",
    "VetoMemory",
    "CollisionRecord",
]
