"""Business-profile tools (read / update the company's own profile).

Both wrap `BusinessProfileRepo` (the same source of truth
`/api/business/profile` uses) so the agent and the UI never drift.

`db_get_business_profile_tool` is a high-value "what do we know about
ourselves" tool — attach it to Adila (operations) and the NEXUS
generalist so any conversation about the company, quotations, or
marketing copy can pull canonical company info instead of inventing it.
"""

import json
from typing import Optional

from crewai.tools import tool

from src.db.repositories.business_profile import BusinessProfileRepo
from src.core.config import logger

ORG_ID = "00000000-0000-0000-0000-000000000001"


def _safe_json(obj, limit: int = 4000) -> str:
    try:
        s = json.dumps(obj, default=str, ensure_ascii=False)
    except Exception:
        s = str(obj)
    if len(s) > limit:
        s = s[:limit] + "... [truncated]"
    return s


@tool("DB Get Business Profile")
def db_get_business_profile_tool() -> str:
    """Read the company's own business profile (company name, industry,
    description, address, phone, email, website, logo URL). Use this
    whenever you need canonical company information — for example when
    drafting marketing copy, a quotation, a contact card, or answering
    a "tell me about the company" question. Never invent these fields;
    always read them from here."""
    try:
        profile = BusinessProfileRepo().get_profile(ORG_ID)
        if not profile:
            return "Profil perniagaan belum dikonfigurasikan. Sila tambah melalui UI Konfigurasi Perniagaan."
        return _safe_json(profile)
    except Exception as e:
        logger.warning(f"db_get_business_profile_tool failed: {e}")
        return f"Error reading business profile: {e}"


@tool("DB Update Business Profile")
def db_update_business_profile_tool(
    company_name: Optional[str] = None,
    industry: Optional[str] = None,
    description: Optional[str] = None,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None,
    logo_url: Optional[str] = None,
) -> str:
    """Update one or more fields of the company's business profile. Only
    pass the fields you want to change — everything else is preserved.
    Returns the full updated profile. Use after the user confirms a
    change to company info (e.g. "tukar nombre kita kepada X")."""
    try:
        profile = BusinessProfileRepo().update(
            ORG_ID,
            company_name=company_name,
            industry=industry,
            description=description,
            address=address,
            phone=phone,
            email=email,
            website=website,
            logo_url=logo_url,
        )
        return _safe_json(profile)
    except Exception as e:
        logger.warning(f"db_update_business_profile_tool failed: {e}")
        return f"Error updating business profile: {e}"
