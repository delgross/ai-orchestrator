import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from agent_runner.executor import ToolExecutor
from agent_runner.state import AgentState

@pytest.fixture
def mock_state():
    state = MagicMock(spec=AgentState)
    state.mcp_servers = {"server1": {"command": "node", "args": ["test.js"]}}
    state.internet_available = True
    state.agent_fs_root = "/tmp/agent_fs"
    return state

@pytest.fixture
def executor(mock_state):
    return ToolExecutor(mock_state)

def test_executor_init(executor):
    assert "list_dir" in executor.tool_impls
    assert "search" in executor.tool_impls
    assert len(executor.tool_definitions) > 0

@pytest.mark.asyncio
async def test_discover_mcp_tools(executor, mock_state):
    with patch("agent_runner.executor.mcp_tools.tool_mcp_proxy", new_callable=AsyncMock) as mock_proxy:
        mock_proxy.return_value = {
            "ok": True,
            "tools": [
                {"name": "test_tool", "description": "A test tool", "inputSchema": {"type": "object"}}
            ]
        }
        
        await executor.discover_mcp_tools()
        
        assert "server1" in executor.mcp_tool_cache
        assert len(executor.mcp_tool_cache["server1"]) == 1
        assert executor.mcp_tool_cache["server1"][0]["function"]["name"] == "test_tool"

@pytest.mark.asyncio
async def test_get_all_tools(executor, mock_state):
    executor.mcp_tool_cache = {
        "time": [{"function": {"name": "get_time", "description": "...", "parameters": {}}}]
    }
    
    tools = await executor.get_all_tools()
    # Check if core tool from MCP is included
    assert any(t["function"]["name"] == "mcp__time__get_time" for t in tools)
    # Check if built-in tool is included
    assert any(t["function"]["name"] == "list_dir" for t in tools)

@pytest.mark.asyncio
async def test_execute_tool_call_local(executor, mock_state):
    # Mock a local tool implementation
    mock_impl = AsyncMock(return_value="file list")
    executor.tool_impls["list_dir"] = mock_impl
    
    tool_call = {
        "function": {
            "name": "list_dir",
            "arguments": '{"path": "."}'
        }
    }
    
    with patch("agent_runner.executor.track_event") as mock_track:
        res = await executor.execute_tool_call(tool_call)
        assert res == {"ok": True, "result": "file list"}
        mock_impl.assert_called_once_with(mock_state, path=".")

@pytest.mark.asyncio
async def test_execute_tool_call_mcp(executor, mock_state):
    tool_call = {
        "function": {
            "name": "mcp__server1__test_tool",
            "arguments": '{"arg1": "val1"}'
        }
    }
    
    with patch("agent_runner.executor.mcp_tools.tool_mcp_proxy", new_callable=AsyncMock) as mock_proxy:
        mock_proxy.return_value = {"ok": True, "result": "mcp result"}
        
        res = await executor.execute_tool_call(tool_call)
        assert res == {"ok": True, "result": "mcp result"}
        mock_proxy.assert_called_once_with(mock_state, "server1", "test_tool", {"arg1": "val1"})
