import pytest
from fastapi.testclient import TestClient
from radar.api.main import app, get_current_user

# Mock authentication
def mock_get_current_user_a():
    return "user_a"

def mock_get_current_user_b():
    return "user_b"

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_parallel_sync_trigger(db_conn, client, monkeypatch):
    """Verify that User B is not blocked when User A has a sync in progress."""
    from radar.storage.db import add_sync_run
    
    # 1. Simulate User A having a running sync in DB
    add_sync_run("user_a", "prod_a", ["sub1"], 3) # status defaults to 'Running' in add_sync_run
    
    # 2. Try to trigger sync as User A (Should fail/block)
    app.dependency_overrides[get_current_user] = mock_get_current_user_a
    response_a = client.post("/api/sync", params={"subreddits": ["sub1"], "days": 3, "product": "prod_a"})
    assert response_a.status_code == 200
    assert "error" in response_a.json()
    assert "already in progress" in response_a.json()["error"]

    # 3. Try to trigger sync as User B (Should succeed)
    app.dependency_overrides[get_current_user] = mock_get_current_user_b
    response_b = client.post("/api/sync", params={"subreddits": ["sub1"], "days": 3, "product": "prod_b"})
    
    # Note: If it says "success", it means the global blocker is gone!
    assert response_b.status_code == 200
    assert "Sync started" in response_b.json()["status"]
    
    # Clean up overrides
    app.dependency_overrides = {}
