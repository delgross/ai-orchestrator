import pytest
from fastapi.testclient import TestClient
from router.router import app, state
import router.config as config

client = TestClient(app)

def test_root_redirect():
    # Root should redirect to dashboard v2
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/v2/index.html" in response.headers["location"]

def test_health_check():
    # Test the explicit /health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "services" in data
    assert "router" in data["services"]
    assert data["services"]["router"]["ok"] is True

def test_v2_dashboard_static():
    # Test that static files are served from /v2
    response = client.get("/v2/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_list_models_unauthorized(monkeypatch):
    # Set a token to test auth
    monkeypatch.setattr(config, "ROUTER_AUTH_TOKEN", "test-token")
    
    response = client.get("/v1/models")
    assert response.status_code == 401
    
    response = client.get("/v1/models", headers={"Authorization": "Bearer wrong"})
    assert response.status_code == 403
    
    response = client.get("/v1/models", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200

def test_stats_protected():
    # Stats should also be protected by auth
    # If ROUTER_AUTH_TOKEN is empty by default in tests, it might pass
    # So we force it
    import router.config as config
    original_token = config.ROUTER_AUTH_TOKEN
    config.ROUTER_AUTH_TOKEN = "stats-token"
    try:
        response = client.get("/stats")
        assert response.status_code == 401
        
        response = client.get("/stats", headers={"Authorization": "Bearer stats-token"})
        assert response.status_code == 200
    finally:
        config.ROUTER_AUTH_TOKEN = original_token
