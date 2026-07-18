import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ai.agents.tool_mappings import (
    get_tools,
    STATIC_TOOL_MAPPINGS,
    _NEXUS_STATIC_TOOLS,
)
from src.ai.tools import (
    product_pricing_tool,
    contact_info_tool,
    conversation_history_tool,
    system_documentation_tool,
    db_upsert_lead_tool,
    workflow_generate_quotation_tool,
    db_get_business_profile_tool,
    db_update_business_profile_tool,
)


# ─── Per-agent tool list ────────────────────────────────────────────────────

def test_every_agent_in_registry_has_a_list():
    from src.core.constants import AGENTS
    for key in AGENTS:
        assert key in STATIC_TOOL_MAPPINGS, f"Agent {key} missing from STATIC_TOOL_MAPPINGS"
        assert isinstance(STATIC_TOOL_MAPPINGS[key], list)


def test_claudia_has_no_execution_tools():
    assert STATIC_TOOL_MAPPINGS["CLAUDIA"] == []


def test_maya_has_pricing_and_workflow_tools():
    maya = STATIC_TOOL_MAPPINGS["MAYA"]
    assert product_pricing_tool in maya
    assert contact_info_tool in maya
    assert conversation_history_tool in maya
    assert db_upsert_lead_tool in maya
    assert workflow_generate_quotation_tool in maya


def test_hakim_has_system_docs():
    assert system_documentation_tool in STATIC_TOOL_MAPPINGS["HAKIM"]


def test_get_tools_for_unknown_key_returns_empty_list():
    assert get_tools("DOES_NOT_EXIST") == []


# ─── Business profile (sole owner = Adila + NEXUS union) ────────────────────

def test_adila_has_business_profile_tools():
    adila = get_tools("ADILA")
    names = {t.name for t in adila}
    assert "DB Get Business Profile" in names
    assert "DB Update Business Profile" in names


def test_only_adila_and_nexus_have_business_profile_tools():
    for key in ("MAYA", "HAKIM", "ZARA", "DANISH", "AIMAN", "AMELIA", "CLAUDIA"):
        names = {t.name for t in get_tools(key)}
        assert "DB Get Business Profile" not in names, f"{key} should not own business profile"
        assert "DB Update Business Profile" not in names, f"{key} should not own business profile"


# ─── Image generation (upstream) ────────────────────────────────────────────

def test_danish_gets_image_tool_only_when_collector_supplied():
    without_collector = get_tools("DANISH", artifact_collector=None)
    with_collector = get_tools("DANISH", artifact_collector=[])

    assert without_collector == [t for t in without_collector if t.name != "Image Generation"]
    assert any(t.name == "Image Generation" for t in with_collector)
    assert len(with_collector) > len(without_collector)


def test_other_agents_never_get_image_tool():
    for agent_key in ["ZARA", "AIMAN", "AMELIA", "ADILA", "CLAUDIA", "MAYA", "HAKIM"]:
        tools = get_tools(agent_key, artifact_collector=[])
        assert all(t.name != "Image Generation" for t in tools), (
            f"{agent_key} unexpectedly has Image Generation tool"
        )


def test_maya_static_tools_unaffected_by_collector():
    maya_tools = get_tools("MAYA", artifact_collector=[])
    assert product_pricing_tool in maya_tools
    assert contact_info_tool in maya_tools
    assert conversation_history_tool in maya_tools
    assert all(t.name != "Image Generation" for t in maya_tools)


# ─── NEXUS generalist fallback ──────────────────────────────────────────────

def test_nexus_is_registered_in_agents_and_specialist_agents():
    from src.core.constants import AGENTS, SPECIALIST_AGENTS
    assert "NEXUS" in AGENTS
    assert "NEXUS" in SPECIALIST_AGENTS


def test_nexus_union_contains_every_other_agents_static_tools():
    """NEXUS gets the deduplicated union of every non-NEXUS agent's static
    list — that's the whole point of the generalist fallback."""
    non_nexus = [
        t for k, tools in STATIC_TOOL_MAPPINGS.items() if k != "NEXUS"
        for t in tools
    ]
    non_nexus_ids = {id(t) for t in non_nexus}
    nexus_ids = {id(t) for t in _NEXUS_STATIC_TOOLS}
    missing = non_nexus_ids - nexus_ids
    assert not missing, f"NEXUS union missing {len(missing)} tools"


def test_nexus_includes_business_profile_and_image_gen():
    nexus = get_tools("NEXUS", artifact_collector=[])
    names = {t.name for t in nexus}
    assert "DB Get Business Profile" in names
    assert "DB Update Business Profile" in names
    assert "Image Generation" in names


def test_nexus_image_gen_gated_by_collector():
    without = get_tools("NEXUS", artifact_collector=None)
    with_coll = get_tools("NEXUS", artifact_collector=[])
    assert not any(t.name == "Image Generation" for t in without)
    assert any(t.name == "Image Generation" for t in with_coll)


def test_nexus_gets_full_browser_set():
    """NEXUS (and Hakim) get every loaded browser tool, not a subset."""
    from src.ai.agents.tool_mappings import _browser_tools
    expected_browser_names = {t.name for t in _browser_tools()}
    nexus_browser_names = {t.name for t in get_tools("NEXUS") if t.name.startswith("Browser ")}
    # Browser tools may be absent if Playwright is not installed — guard for that.
    if expected_browser_names:
        assert nexus_browser_names == expected_browser_names


def test_nexus_has_more_tools_than_any_specialist():
    """NEXUS is the generalist — it must have the largest tool list."""
    nexus_count = len(get_tools("NEXUS"))
    for key in ("MAYA", "HAKIM", "ZARA", "DANISH", "AIMAN", "AMELIA", "ADILA"):
        assert nexus_count > len(get_tools(key)), (
            f"NEXUS ({nexus_count}) should have more tools than {key}"
        )
