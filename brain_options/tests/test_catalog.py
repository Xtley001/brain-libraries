"""
Unit tests — brain_options.catalog
"""
from brain_options.catalog import OptionsCatalog, OptionField


def test_catalog_loads_fields():
    cat = OptionsCatalog()
    assert len(cat.fields) > 0
    f = cat.get_field("forward_price_30")
    assert f is not None
    assert isinstance(f, OptionField)
    assert f.id == "forward_price_30"


def test_catalog_subfamilies():
    cat = OptionsCatalog()
    subfams = cat.subfamilies()
    assert len(subfams) > 0
