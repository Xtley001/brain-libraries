"""Unit tests — brain_sentiment.catalog"""
from brain_sentiment.catalog import SentimentCatalog, SentimentField


def test_catalog_loads_fields():
    cat = SentimentCatalog()
    assert len(cat.fields) > 0
    f = cat.get_field("snt1_d1_netearningsrevision")
    assert f is not None
    assert isinstance(f, SentimentField)
    assert f.id == "snt1_d1_netearningsrevision"


def test_all_field_ids():
    cat = SentimentCatalog()
    ids = cat.all_field_ids
    assert "snt1_d1_netearningsrevision" in ids
