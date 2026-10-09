"""Unit tests — brain_risk_model.catalog"""
from brain_risk_model.catalog import RiskModelCatalog, RiskModelField


def test_catalog_loads_fields():
    cat = RiskModelCatalog()
    assert len(cat.fields) > 0
    f = cat.get_field("beta_last_60_days_spy")
    assert f is not None
    assert isinstance(f, RiskModelField)
    assert f.id == "beta_last_60_days_spy"


def test_all_field_ids():
    cat = RiskModelCatalog()
    ids = cat.all_field_ids
    assert "beta_last_60_days_spy" in ids
