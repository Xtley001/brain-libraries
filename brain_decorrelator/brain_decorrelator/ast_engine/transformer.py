"""
AST Structural Transformer.
Applies syntax-tree mutations, parameter scaling, and structural transformations.
"""
from __future__ import annotations

import copy
from typing import Callable, List, Optional
from brain_decorrelator.ast_engine.parser import ASTNode


class ASTTransformer:
    """Provides subtree mutation, wrapping, and operator replacement on ASTs."""

    @staticmethod
    def replace_identifier(root: ASTNode, target_name: str, replacement_node: ASTNode) -> ASTNode:
        """Deep copies root and replaces all occurrences of target_name with replacement_node."""
        node = copy.deepcopy(root)

        def _traverse(curr: ASTNode) -> ASTNode:
            if curr.node_type == "identifier" and curr.value == target_name:
                return copy.deepcopy(replacement_node)
            curr.args = [_traverse(child) for child in curr.args]
            return curr

        return _traverse(node)

    @staticmethod
    def replace_call(root: ASTNode, call_name: str, new_call_name: str) -> ASTNode:
        """Deep copies root and replaces all call names matching call_name."""
        node = copy.deepcopy(root)

        def _traverse(curr: ASTNode) -> ASTNode:
            if curr.node_type == "call" and curr.value == call_name:
                curr.value = new_call_name
            curr.args = [_traverse(child) for child in curr.args]
            return curr

        return _traverse(node)

    @staticmethod
    def wrap_in_call(root: ASTNode, wrapper_func: str, extra_args: Optional[List[ASTNode]] = None) -> ASTNode:
        """Wraps root as the first argument in wrapper_func(root, *extra_args)."""
        args = [copy.deepcopy(root)]
        if extra_args:
            args.extend(copy.deepcopy(extra_args))
        return ASTNode(node_type="call", value=wrapper_func, args=args)
