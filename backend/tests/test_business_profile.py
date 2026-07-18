import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_get_profile_flattens_name_and_settings():
    from src.db.repositories.business_profile import BusinessProfileRepo

    fake_db = MagicMock()
    fake_db.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
        data={
            "id": "org-1",
            "name": "Acme Sdn Bhd",
            "settings": {
                "industry": "F&B",
                "description": "Goreng pisang specialist",
                "address": "Jalan Tun Razak",
                "phone": "+60123456789",
                "email": "hi@acme.test",
                "website": "https://acme.test",
                "logo_url": "https://acme.test/logo.png",
            },
        }
    )
    with patch("src.db.repositories.business_profile.get_supabase", return_value=fake_db):
        repo = BusinessProfileRepo()
        profile = repo.get_profile("org-1")

    assert profile == {
        "company_name": "Acme Sdn Bhd",
        "industry": "F&B",
        "description": "Goreng pisang specialist",
        "address": "Jalan Tun Razak",
        "phone": "+60123456789",
        "email": "hi@acme.test",
        "website": "https://acme.test",
        "logo_url": "https://acme.test/logo.png",
    }


def test_get_profile_returns_none_when_org_missing():
    from src.db.repositories.business_profile import BusinessProfileRepo

    fake_db = MagicMock()
    fake_db.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
        data=None
    )
    with patch("src.db.repositories.business_profile.get_supabase", return_value=fake_db):
        repo = BusinessProfileRepo()
        assert repo.get_profile("org-x") is None


def test_update_merges_settings_and_preserves_unspecified_fields():
    from src.db.repositories.business_profile import BusinessProfileRepo

    fake_db = MagicMock()
    # First .select() call (in .get) returns existing org
    select_chain = fake_db.table.return_value.select.return_value
    select_chain.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
        data={
            "id": "org-1",
            "name": "Old Name",
            "settings": {
                "industry": "F&B",
                "description": "old desc",
                "phone": "+60111111111",
            },
        }
    )
    # .update() -> .eq() -> .execute() returns updated row
    update_chain = fake_db.table.return_value.update.return_value
    update_chain.eq.return_value.execute.return_value = MagicMock(
        data=[{
            "id": "org-1",
            "name": "New Name",
            "settings": {
                "industry": "F&B",
                "description": "new desc",
                "phone": "+60111111111",
            },
        }]
    )

    with patch("src.db.repositories.business_profile.get_supabase", return_value=fake_db):
        repo = BusinessProfileRepo()
        profile = repo.update("org-1", company_name="New Name", description="new desc")

    assert profile["company_name"] == "New Name"
    assert profile["description"] == "new desc"
    # Industry + phone untouched
    assert profile["industry"] == "F&B"
    assert profile["phone"] == "+60111111111"


def test_update_raises_when_org_missing():
    from src.db.repositories.business_profile import BusinessProfileRepo

    fake_db = MagicMock()
    fake_db.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
        data=None
    )
    with patch("src.db.repositories.business_profile.get_supabase", return_value=fake_db):
        repo = BusinessProfileRepo()
        try:
            repo.update("org-x", company_name="X")
        except LookupError:
            return
        raise AssertionError("expected LookupError when org missing")


def test_get_business_profile_tool_is_wired_into_tools_init():
    from src.ai.tools import db_get_business_profile_tool, db_update_business_profile_tool
    assert db_get_business_profile_tool.name == "DB Get Business Profile"
    assert db_update_business_profile_tool.name == "DB Update Business Profile"


def test_db_get_business_profile_tool_handles_missing_org():
    from src.ai.tools.business_profile import db_get_business_profile_tool

    fake_db = MagicMock()
    fake_db.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
        data=None
    )
    with patch("src.db.repositories.business_profile.get_supabase", return_value=fake_db):
        result = db_get_business_profile_tool.run()

    # Returns a human-readable string the LLM can act on.
    assert "belum dikonfigurasikan" in result or "not found" in result.lower()
