from fastapi.testclient import TestClient
from router.app import create_app
from router.config import state

app = create_app()
client = TestClient(app)

def test_health_check():
    # Explicitly request JSON to avoid redirect to dashboard
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "version" in data

def test_dashboard_access():
    # Dashboard is served as static file or redirect
    response = client.get("/dashboard")
    # It usually returns a FileResponse (200) or Redirect
    assert response.status_code in [200, 307]

def test_list_models_empty(monkeypatch):
    # Mock state.providers to be empty
    monkeypatch.setattr(state, "providers", {})
    # Mock clear cache
    state.models_cache = (0.0, {})
    
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    # Should at least contain agent:mcp if enabled in code, or be empty
    # But filters might apply.
    assert isinstance(data["data"], list)

def test_auth_middleware(monkeypatch):
    monkeypatch.setattr("router.router.ROUTER_AUTH_TOKEN", "secret-token")
    
    # Request without token to protected endpoint
    response = client.get("/v1/models")
    assert response.status_code == 401
    
    # Request with wrong token
    response = client.get("/v1/models", headers={"Authorization": "Bearer wrong"})
    assert response.status_code == 403
    
    # Request with correct token
    # We mock providers to avoid actual network calls during auth check
    monkeypatch.setattr(state, "providers", {})
    response = client.get("/v1/models", headers={"Authorization": "Bearer secret-token"})
    assert response.status_code == 200
