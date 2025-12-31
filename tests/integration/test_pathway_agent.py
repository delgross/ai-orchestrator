import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from agent_runner.engine import AgentEngine
from agent_runner.state import AgentState

@pytest.fixture
def mock_state():
    state = MagicMock(spec=AgentState)
    state.agent_model = "gpt-4o-mini"
    state.gateway_base = "http://localhost:8000"
    state.router_auth_token = "test_token"
    state.http_timeout = 5.0
    state.mcp_circuit_breaker = MagicMock()
    state.mcp_circuit_breaker.is_allowed.return_value = True
    state.get_http_client = AsyncMock()
    state.max_tool_steps = 3
    state.internet_available = True
    state.fallback_model = "ollama:llama3.3"
    state.fallback_enabled = False
    state.finalizer_enabled = False
    state.finalizer_model = "gpt-4o"
    return state

@pytest.fixture
def engine(mock_state):
    return AgentEngine(mock_state)

@pytest.mark.asyncio
async def test_full_agent_pathway(engine, mock_state):
    """Test full flow: User Message -> Tool Call -> Tool Result -> Final Answer."""
    
    mock_client = AsyncMock()
    mock_state.get_http_client.return_value = mock_client
    
    # Sequence of responses from the model gateway
    # 1. Tool Call for 'list_dir'
    # 2. Final Answer
    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Let me check the files.",
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {"name": "list_dir", "arguments": '{"path": "."}'}
                }]
            }
        }]
    }
    
    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "I see the files: main.py, engine.py."
            }
        }]
    }
    
    mock_client.post.side_effect = [resp1, resp2]
    
    # Mock system prompt and tool gathering
    with patch.object(engine, "get_system_prompt", return_value="System instructions."), \
         patch.object(engine, "get_all_tools", return_value=[{"function": {"name": "list_dir"}}]):
        
        # Mock tool execution
        engine.executor.execute_tool_call = AsyncMock(return_value={"ok": True, "result": "main.py, engine.py"})
        
        user_messages = [{"role": "user", "content": "What files are here?"}]
        response = await engine.agent_loop(user_messages)
        
        assert "I see the files" in response["choices"][0]["message"]["content"]
        assert engine.executor.execute_tool_call.called
        assert mock_client.post.call_count == 2
