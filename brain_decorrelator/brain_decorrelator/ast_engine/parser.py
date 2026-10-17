"""
Fast Expression AST Parser & Serializer.
Parses WorldQuant BRAIN mathematical expressions into structured AST nodes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union


@dataclass
class ASTNode:
    """Represents a node in the expression syntax tree."""
    node_type: str  # "call", "binary_op", "unary_op", "identifier", "literal"
    value: Union[str, float, int]
    args: List[ASTNode] = field(default_factory=list)

    def to_expr(self) -> str:
        """Serializes the AST node back to a valid Fast Expression string."""
        if self.node_type == "literal":
            if isinstance(self.value, float):
                return f"{self.value:g}"
            return str(self.value)
        elif self.node_type == "identifier":
            return str(self.value)
        elif self.node_type == "unary_op":
            arg = self.args[0].to_expr() if self.args else ""
            return f"-{arg}"
        elif self.node_type == "binary_op":
            left = self.args[0].to_expr() if len(self.args) > 0 else ""
            right = self.args[1].to_expr() if len(self.args) > 1 else ""
            return f"({left} {self.value} {right})"
        elif self.node_type == "call":
            args_str = ", ".join(arg.to_expr() for arg in self.args)
            return f"{self.value}({args_str})"
        return str(self.value)

    def signature(self) -> str:
        """Structural signature of this subtree for motif matching."""
        if self.node_type == "call":
            sub_sigs = ",".join(arg.signature() for arg in self.args)
            return f"{self.value}({sub_sigs})"
        elif self.node_type == "binary_op":
            left = self.args[0].signature() if len(self.args) > 0 else "?"
            right = self.args[1].signature() if len(self.args) > 1 else "?"
            return f"({left}{self.value}{right})"
        return self.node_type


class ASTParser:
    """Recursive descent tokenizer & parser for financial fast expressions."""

    TOKEN_SPEC = [
        ("NUMBER", r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"),
        ("BOOL_OP", r"&&|\|\|"),
        ("COMP_OP", r"<=|>=|==|!=|<|>"),
        ("ARITH_OP", r"[+\-*/]"),
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("COMMA", r","),
        ("WS", r"\s+"),
    ]
    TOKEN_REGEX = re.compile("|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in TOKEN_SPEC))

    def parse(self, expr: str) -> ASTNode:
        tokens = []
        for mo in self.TOKEN_REGEX.finditer(expr):
            kind = mo.lastgroup
            val = mo.group()
            if kind == "WS":
                continue
            tokens.append((kind, val))

        if not tokens:
            raise ValueError(f"Empty expression: {expr!r}")

        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else (None, None)

        def consume(expected_kind=None):
            nonlocal pos
            tok = tokens[pos]
            if expected_kind and tok[0] != expected_kind:
                raise SyntaxError(f"Expected {expected_kind}, got {tok} at position {pos}")
            pos += 1
            return tok

        def parse_expression() -> ASTNode:
            return parse_logic_or()

        def parse_logic_or() -> ASTNode:
            node = parse_logic_and()
            while pos < len(tokens) and tokens[pos][1] == "||":
                op = consume()[1]
                right = parse_logic_and()
                node = ASTNode(node_type="binary_op", value=op, args=[node, right])
            return node

        def parse_logic_and() -> ASTNode:
            node = parse_comparison()
            while pos < len(tokens) and tokens[pos][1] == "&&":
                op = consume()[1]
                right = parse_comparison()
                node = ASTNode(node_type="binary_op", value=op, args=[node, right])
            return node

        def parse_comparison() -> ASTNode:
            node = parse_arith_add_sub()
            while pos < len(tokens) and tokens[pos][0] == "COMP_OP":
                op = consume()[1]
                right = parse_arith_add_sub()
                node = ASTNode(node_type="binary_op", value=op, args=[node, right])
            return node

        def parse_arith_add_sub() -> ASTNode:
            node = parse_arith_mul_div()
            while pos < len(tokens) and tokens[pos][1] in ("+", "-"):
                op = consume()[1]
                right = parse_arith_mul_div()
                node = ASTNode(node_type="binary_op", value=op, args=[node, right])
            return node

        def parse_arith_mul_div() -> ASTNode:
            node = parse_unary()
            while pos < len(tokens) and tokens[pos][1] in ("*", "/"):
                op = consume()[1]
                right = parse_unary()
                node = ASTNode(node_type="binary_op", value=op, args=[node, right])
            return node

        def parse_unary() -> ASTNode:
            if pos < len(tokens) and tokens[pos][1] == "-":
                consume()
                operand = parse_primary()
                if operand.node_type == "literal" and isinstance(operand.value, (int, float)):
                    return ASTNode(node_type="literal", value=-operand.value)
                return ASTNode(node_type="unary_op", value="-", args=[operand])
            return parse_primary()

        def parse_primary() -> ASTNode:
            nonlocal pos
            kind, val = peek()
            if kind == "LPAREN":
                consume("LPAREN")
                expr_node = parse_expression()
                consume("RPAREN")
                return expr_node
            elif kind == "NUMBER":
                consume("NUMBER")
                val_num = float(val) if "." in val or "e" in val.lower() else int(val)
                return ASTNode(node_type="literal", value=val_num)
            elif kind == "IDENT":
                ident_tok = consume("IDENT")[1]
                if pos < len(tokens) and tokens[pos][0] == "LPAREN":
                    # Function call
                    consume("LPAREN")
                    call_args = []
                    if pos < len(tokens) and tokens[pos][0] != "RPAREN":
                        call_args.append(parse_expression())
                        while pos < len(tokens) and tokens[pos][0] == "COMMA":
                            consume("COMMA")
                            call_args.append(parse_expression())
                    consume("RPAREN")
                    return ASTNode(node_type="call", value=ident_tok, args=call_args)
                return ASTNode(node_type="identifier", value=ident_tok)
            raise SyntaxError(f"Unexpected token {kind} ({val}) at {pos}")

        root = parse_expression()
        return root


def parse_ast(expr: str) -> ASTNode:
    """Convenience helper to parse an expression into an AST."""
    return ASTParser().parse(expr)


def unparse_ast(node: ASTNode) -> str:
    """Convenience helper to unparse an AST back into an expression string."""
    return node.to_expr()
