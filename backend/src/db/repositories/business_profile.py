"""Repository for the `organizations` row used as the company's business
profile (company name + `settings` JSON holding industry, description,
address, phone, email, website, logo_url). Used by both
`/api/business/profile` (UI) and the `db_*_business_profile_tool` CrewAI
tools — single source of truth for the schema.
"""

from typing import Optional

from src.db.client import get_supabase


class BusinessProfileRepo:
    """Read/update the organisation's business profile. The profile is the
    `organizations.name` field plus the `settings` JSONB column; keep the
    two consistent by always going through this repo (so we don't
    accidentally write to one and not the other)."""

    def __init__(self):
        self._db = get_supabase()

    def get(self, org_id: str) -> Optional[dict]:
        """Return the full org row or None. The shape of the response:
        `{id, name, settings: {industry, description, address, phone,
        email, website, logo_url}, ...}`."""
        result = (
            self._db.table("organizations")
            .select("*")
            .eq("id", org_id)
            .maybe_single()
            .execute()
        )
        return result.data

    def get_profile(self, org_id: str) -> Optional[dict]:
        """Return just the business-profile view (flattened `name` +
        `settings` fields) instead of the raw row. Same shape as
        `/api/business/profile` GET."""
        org = self.get(org_id)
        if not org:
            return None
        return _flatten(org)

    def update(self, org_id: str, *, company_name: Optional[str] = None,
               industry: Optional[str] = None, description: Optional[str] = None,
               address: Optional[str] = None, phone: Optional[str] = None,
               email: Optional[str] = None, website: Optional[str] = None,
               logo_url: Optional[str] = None) -> dict:
        """Update any subset of the profile fields. Only fields explicitly
        passed are written; everything else is preserved.

        Returns the updated flattened profile (same shape as `get_profile`)."""
        org = self.get(org_id)
        if not org:
            raise LookupError(f"Organization '{org_id}' not found")

        updates: dict = {}
        if company_name is not None:
            updates["name"] = company_name

        settings = dict(org.get("settings") or {})
        for field in ("industry", "description", "address", "phone", "email", "website", "logo_url"):
            val = locals()[field]
            if val is not None:
                settings[field] = val
        if settings.keys() - {"industry", "description", "address", "phone", "email", "website", "logo_url"}:
            updates["settings"] = settings
        else:
            # Always write settings if we touched it, even if only to update
            # one of the known fields — keeps the JSONB in sync.
            if any(locals().get(f) is not None for f in
                   ("industry", "description", "address", "phone", "email", "website", "logo_url")):
                updates["settings"] = settings

        if not updates:
            return _flatten(org)

        result = (
            self._db.table("organizations")
            .update(updates)
            .eq("id", org_id)
            .execute()
        )
        updated = result.data[0] if result.data else org
        return _flatten(updated)


def _flatten(org: dict) -> dict:
    settings = org.get("settings") or {}
    return {
        "company_name": org.get("name", ""),
        "industry": settings.get("industry", ""),
        "description": settings.get("description", ""),
        "address": settings.get("address", ""),
        "phone": settings.get("phone", ""),
        "email": settings.get("email", ""),
        "website": settings.get("website", ""),
        "logo_url": settings.get("logo_url", ""),
    }
