import pytest
from common.error_utils import get_error_message, create_error_response, ErrorCode, get_error_suggestions

def test_get_error_message_standard():
    e = ValueError("something went wrong")
    assert get_error_message(e) == "something went wrong"

def test_get_error_message_blank(caplog):
    # Blank error message should trigger an error log
    e = ValueError("")
    msg = get_error_message(e, context="test_context")
    assert msg == "ValueError"
    assert "BLANK ERROR MESSAGE DETECTED" in caplog.text
    # Check extra context in records
    assert any(getattr(record, "context", None) == "test_context" for record in caplog.records)

def test_create_error_response():
    resp = create_error_response(
        code=ErrorCode.VALIDATION_ERROR,
        category="test",
        message="invalid input",
        details={"field": "name"},
        suggestions=["try again"]
    )
    assert resp["ok"] is False
    assert resp["error"]["code"] == "VALIDATION_ERROR"
    assert resp["error"]["message"] == "invalid input"
    assert resp["error"]["details"]["field"] == "name"
    assert "try again" in resp["error"]["suggestions"]
    assert "timestamp" in resp["error"]

def test_get_error_suggestions():
    sug = get_error_suggestions(ErrorCode.CONFIG_ERROR)
    assert any("config.yaml" in s for s in sug)
    
    sug_mcp = get_error_suggestions(ErrorCode.MCP_SERVER_NOT_FOUND, context={"server": "my-server"})
    assert any("my-server" in s for s in sug_mcp)
