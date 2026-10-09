"""
Unit tests — brain_core.llm (clean_json_array and LLMAdapter)
"""
from brain_core.config import Config
from brain_core.llm import LLMAdapter, clean_json_array


def test_clean_json_array_markdown_fenced():
    raw = """Here is the result:
```json
[
  {"expression": "rank(close)", "archetype": "momentum"},
  {"expression": "ts_delta(volume, 5)", "archetype": "volume"}
]
```
Hope this helps!"""
    res = clean_json_array(raw)
    assert len(res) == 2
    assert res[0]["expression"] == "rank(close)"
    assert res[1]["archetype"] == "volume"


def test_clean_json_array_trailing_commas():
    raw = """[
        {"expression": "rank(vwap)", "decay": 10,},
    ]"""
    res = clean_json_array(raw)
    assert len(res) == 1
    assert res[0]["expression"] == "rank(vwap)"


def test_clean_json_array_truncated_stream_recovery():
    raw = """Analyzing factors...
    [
        {"expression": "rank(open - close)", "archetype": "reversal"},
        {"expression": "ts_mean(returns, 20)", "archetype": "trend"},
        {"expression": "correlat
    """
    res = clean_json_array(raw)
    assert len(res) == 2
    assert res[0]["expression"] == "rank(open - close)"
    assert res[1]["expression"] == "ts_mean(returns, 20)"


def test_llm_adapter_rotate_keys():
    cfg = Config(groq_keys=["keyA", "keyB", "keyC"])
    adapter = LLMAdapter(cfg)
    k1 = adapter._rotate_keys("groq", cfg.groq_keys)
    k2 = adapter._rotate_keys("groq", cfg.groq_keys)
    k3 = adapter._rotate_keys("groq", cfg.groq_keys)

    assert k1 == ["keyA", "keyB", "keyC"]
    assert k2 == ["keyB", "keyC", "keyA"]
    assert k3 == ["keyC", "keyA", "keyB"]
