import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ai.agents.registry import load_agent, load_agents
from src.core.constants import AGENTS, SPECIALIST_AGENTS


def test_load_agents_returns_all_agents():
    configs = load_agents()
    assert set(configs.keys()) == set(AGENTS.keys())
    # 8 original specialists + CLAUDIA (router) + NEXUS (generalist) = 9.
    assert len(configs) == len(AGENTS)


def test_load_agents_defaults_to_openai_provider():
    configs = load_agents()
    for key, config in configs.items():
        assert config.provider == "openai"
        assert config.model


def test_load_agent_single_specialist():
    config = load_agent("ZARA")
    assert config.key == "ZARA"
    assert config.name == "Zara"
    assert "Kewangan" in config.role


def test_load_agent_lowercase_key_normalized():
    assert load_agent("zara").key == "ZARA"


def test_load_agent_unknown_key_raises():
    with pytest.raises(KeyError):
        load_agent("NOBODY")


def test_load_agent_propagates_org_id():
    config = load_agent("MAYA", org_id="org-123")
    assert config.org_id == "org-123"


def test_specialist_agents_excludes_claudia():
    configs = load_agents()
    specialist_configs = {k: v for k, v in configs.items() if k in SPECIALIST_AGENTS}
    assert "CLAUDIA" not in specialist_configs
    # Specialists = all 7 originals + NEXUS (the generalist fallback that
    # TaskExecutionFlow can route to). Total is len(AGENTS) - 1 (no Claudia).
    assert len(specialist_configs) == len(AGENTS) - 1
