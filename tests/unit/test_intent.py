import pytest
import dataclasses
from unittest.mock import AsyncMock, patch, MagicMock
from agent_runner.intent import extract_text_content, classify_search_intent, generate_search_query

@pytest.fixture
def mock_state():
    state = MagicMock()
    state.agent_model = "gpt-4o-mini"
    state.gateway_base = "http://localhost:8000"
    return state

def test_extract_text_content_string():
    assert extract_text_content("hello") == "hello"

def test_extract_text_content_list():
    content = [
        {"type": "text", "text": "hello"},
        {"type": "image", "image": "base64..."},
        {"type": "text", "text": "world"}
    ]
    assert extract_text_content(content) == "hello world"

def test_extract_text_content_other():
    assert extract_text_content(123) == "123"

@pytest.mark.asyncio
async def test_classify_search_intent_success(mock_state):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"target_servers": ["server1"]}'}}]
        }
        mock_post.return_value = mock_resp
        
        # Patch recursive dependency
        with patch("agent_runner.feedback.get_suggested_servers", new_callable=AsyncMock) as mock_feedback:
            mock_feedback.return_value = ["server1"]
            
            res = await classify_search_intent("some query", mock_state, "server1: tool1")
            assert res == {"target_servers": ["server1"]}
            mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_classify_search_intent_fallback(mock_state):
    # No menu available
    res = await classify_search_intent("query", mock_state, "")
    assert res == {"target_servers": [], "notes": "No menu available"}

@pytest.mark.asyncio
async def test_generate_search_query_success(mock_state):
    messages = [
        {"role": "user", "content": "What is the weather in Paris?"}
    ]
    
    async def mock_call_gateway(messages, model, tools):
        return {
            "choices": [{"message": {"content": '"weather Paris"'}}]
        }
    
    with patch("agent_runner.intent.extract_text_content", return_value="What is the weather in Paris?"):
        res = await generate_search_query(messages, mock_state, mock_call_gateway)
        assert res == "weather Paris"

@pytest.mark.asyncio
async def test_generate_search_query_no_user_msg(mock_state):
    messages = [{"role": "system", "content": "hi"}]
    res = await generate_search_query(messages, mock_state, AsyncMock())
    assert res == ""
