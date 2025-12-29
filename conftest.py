import sys
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("ROUTER_AUTH_TOKEN", "")
    monkeypatch.setenv("PROVIDERS_YAML", str(PROJECT_ROOT / "tests/integration/test_providers.yaml"))
