import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agent_runner.engine import AgentEngine
from agent_runner.state import AgentState

@pytest.fixture
def mock_state():
    state = MagicMock(spec=AgentState)
    state.agent_model = "gpt-4o-mini"
    state.fallback_model = "ollama:llama3"
    state.fallback_enabled = True
    state.internet_available = True
    state.mcp_servers = {}
    state.mcp_circuit_breaker = MagicMock()
    state.mcp_circuit_breaker.is_allowed.return_value = True
    state.router_auth_token = "dummy_token"
    state.gateway_base = "http://localhost:8000"
    state.http_timeout = 10.0
    state.get_http_client = AsyncMock()
    return state

@pytest.fixture
def engine(mock_state):
    return AgentEngine(mock_state)

@pytest.mark.asyncio
async def test_engine_delegation_discover(engine):
    engine.executor.discover_mcp_tools = AsyncMock()
    await engine.discover_mcp_tools()
    engine.executor.discover_mcp_tools.assert_called_once()

@pytest.mark.asyncio
async def test_engine_delegation_get_tools(engine):
    engine.executor.get_all_tools = AsyncMock(return_value=[])
    res = await engine.get_all_tools()
    assert res == []
    engine.executor.get_all_tools.assert_called_once()

@pytest.mark.asyncio
async def test_call_gateway_with_tools_success(engine, mock_state):
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
    mock_client.post.return_value = mock_resp
    mock_state.get_http_client.return_value = mock_client
    
    res = await engine.call_gateway_with_tools(messages=[{"role": "user", "content": "hi"}])
    assert res["choices"][0]["message"]["content"] == "hi"
    mock_client.post.assert_called_once()
