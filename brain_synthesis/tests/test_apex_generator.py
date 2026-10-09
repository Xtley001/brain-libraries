"""
Unit tests — brain_synthesis.apex_generator
"""
from brain_synthesis.apex_generator import ApexCandidate, generate_apex_candidates


def test_generate_apex_candidates():
    candidates = generate_apex_candidates()
    assert len(candidates) > 0
    c0 = candidates[0]
    assert isinstance(c0, ApexCandidate)
    assert c0.universe in ("TOP3000", "TOP2000")
    assert c0.neutralization in ("SUBINDUSTRY", "SECTOR")
    assert c0.decay in (10, 12, 15)
    assert "group_neutralize(" in c0.expression


def test_apex_candidates_have_multiple_archetypes():
    candidates = generate_apex_candidates()
    archetypes = {c.archetype_name for c in candidates}
    assert len(archetypes) == 5
    assert "Apex1_Accumulation_Triple" in archetypes
    assert "Apex2_SUE_Smirk_Confluence" in archetypes
    assert "Apex3_Target_Term_Slope" in archetypes
    assert "Apex4_Torpedo_Quality_Drift" in archetypes
    assert "Apex5_LowRisk_Attention_Asymmetry" in archetypes
