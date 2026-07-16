import secrets
from datetime import datetime, timedelta

# In-memory active sessions storage: { token: created_at_datetime }
ACTIVE_SESSIONS = {}

def create_session() -> str:
    """Generate a new secure session token and store it."""
    session_token = secrets.token_hex(16)
    ACTIVE_SESSIONS[session_token] = datetime.now()
    return session_token

def verify_session(session_token: str | None) -> bool:
    """Check if the session token is active and not expired (24 hours)."""
    if not session_token or session_token not in ACTIVE_SESSIONS:
        return False
        
    created_at = ACTIVE_SESSIONS[session_token]
    # Check if session is older than 24 hours
    if datetime.now() - created_at > timedelta(hours=24):
        # Session expired, clean up
        del ACTIVE_SESSIONS[session_token]
        return False
        
    return True

def destroy_session(session_token: str | None) -> None:
    """Remove session token if it exists."""
    if session_token and session_token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[session_token]

