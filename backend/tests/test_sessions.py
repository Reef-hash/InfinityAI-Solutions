import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sessions import create_session, verify_session, destroy_session

def test_session_flow():
    # 1. Create a session
    token = create_session()
    assert token is not None
    assert len(token) > 0
    
    # 2. Verify it is valid
    assert verify_session(token) is True
    
    # 3. Verify an invalid token is False
    assert verify_session("invalid-token") is False
    assert verify_session("") is False
    assert verify_session(None) is False
    
    # 4. Destroy it
    destroy_session(token)
    
    # 5. Verify it is no longer valid
    assert verify_session(token) is False

def test_session_expiration(monkeypatch):
    from datetime import datetime, timedelta
    import src.core.sessions
    
    # Create a session
    token = src.core.sessions.create_session()
    assert src.core.sessions.verify_session(token) is True
    
    # Fake time shift to 25 hours later
    fake_now = datetime.now() + timedelta(hours=25)
    
    class FakeDateTime:
        @classmethod
        def now(cls):
            return fake_now
            
    monkeypatch.setattr(src.core.sessions, "datetime", FakeDateTime)
    
    # Verify that the session is now expired
    assert src.core.sessions.verify_session(token) is False
