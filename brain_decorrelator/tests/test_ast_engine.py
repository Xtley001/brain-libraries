"""
Unit tests for brain_decorrelator.ast_engine
"""
from brain_decorrelator.ast_engine.parser import ASTNode, parse_ast, unparse_ast
from brain_decorrelator.ast_engine.diff import compute_ast_hash, find_differing_subtrees, extract_motif_signature
from brain_decorrelator.ast_engine.transformer import ASTTransformer


def test_parse_and_unparse_simple_call():
    expr = "ts_decay_linear(close, 10)"
    node = parse_ast(expr)
    assert node.node_type == "call"
    assert node.value == "ts_decay_linear"
    assert len(node.args) == 2
    assert node.args[0].node_type == "identifier"
    assert node.args[0].value == "close"
    assert node.args[1].node_type == "literal"
    assert node.args[1].value == 10

    unparsed = unparse_ast(node)
    assert unparsed == "ts_decay_linear(close, 10)"


def test_parse_nested_arithmetic_and_logic():
    expr = "group_neutralize(rank((close - open) / (high + 0.001)), subindustry)"
    node = parse_ast(expr)
    assert node.node_type == "call"
    assert node.value == "group_neutralize"

    unparsed = unparse_ast(node)
    assert "close - open" in unparsed
    assert "subindustry" in unparsed


def test_ast_diff_and_signature():
    ast1 = parse_ast("ts_decay_linear(close, 10)")
    ast2 = parse_ast("ts_decay_linear(volume, 10)")

    diffs = find_differing_subtrees(ast1, ast2)
    assert len(diffs) == 1
    diff_a, diff_b = diffs[0]
    assert diff_a.value == "close"
    assert diff_b.value == "volume"

    sig = extract_motif_signature(ast1)
    assert "ts_decay_linear" in sig


def test_ast_transformer_replace_identifier():
    root = parse_ast("ts_delta(close, 5)")
    new_root = ASTTransformer.replace_identifier(root, "close", ASTNode("identifier", "implied_volatility_30"))
    assert unparse_ast(new_root) == "ts_delta(implied_volatility_30, 5)"


def test_ast_transformer_wrap():
    root = parse_ast("rank(close)")
    wrapped = ASTTransformer.wrap_in_call(root, "group_neutralize", [ASTNode("identifier", "sector")])
    assert unparse_ast(wrapped) == "group_neutralize(rank(close), sector)"
