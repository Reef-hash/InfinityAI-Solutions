import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_nexus_is_in_agents_dict():
    from src.core.constants import AGENTS
    assert "NEXUS" in AGENTS
    assert AGENTS["NEXUS"]["role"] == "Generalist (Semua Alat)"


def test_nexus_is_in_specialist_agents_list():
    """NEXUS must be a specialist (not a router) so TaskExecutionFlow can
    route assignments to it the same as Maya, Hakim, etc."""
    from src.core.constants import SPECIALIST_AGENTS
    assert "NEXUS" in SPECIALIST_AGENTS


def test_claudia_backstory_lists_per_agent_capability_table():
    """The whole point of the rewrite: Claudia must be able to reason
    about which agent has which tool. Grep for key signals."""
    from src.ai.prompts.loader import resolve_role_goal_backstory
    _, _, backstory = resolve_role_goal_backstory("CLAUDIA")
    upper = backstory.upper()
    # Each specialist + NEXUS must be named.
    for name in ("AIMAN", "MAYA", "DANISH", "ZARA", "ADILA", "HAKIM", "NEXUS", "AMELIA"):
        assert name in upper, f"Claudia backstory missing capability entry for {name}"
    # The capability table must mention at least the major tool categories.
    for keyword in ("BROWSER", "PROFIL PERNIAGAAN", "IMAGE GENERATION", "MCP"):
        assert keyword in upper, f"Claudia backstory missing capability keyword: {keyword}"


def test_nexus_backstory_says_generalist_fallback():
    from src.ai.prompts.loader import resolve_role_goal_backstory
    role, goal, backstory = resolve_role_goal_backstory("NEXUS")
    assert "Nexus" in role
    assert "FALLBACK" in backstory.upper() or "GENERALIST" in backstory.upper()


def test_adila_backstory_mentions_business_profile():
    from src.ai.prompts.loader import resolve_role_goal_backstory
    _, _, backstory = resolve_role_goal_backstory("ADILA")
    assert "profil perniagaan" in backstory.lower()


def test_hakim_backstory_mentions_browser_tools():
    from src.ai.prompts.loader import resolve_role_goal_backstory
    _, _, backstory = resolve_role_goal_backstory("HAKIM")
    assert "browser" in backstory.lower() or "playwright" in backstory.lower()


def test_resolve_unknown_agent_raises_keyerror():
    from src.ai.prompts.loader import resolve_role_goal_backstory
    try:
        resolve_role_goal_backstory("DOES_NOT_EXIST")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown agent")
