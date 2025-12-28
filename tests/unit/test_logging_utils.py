import pytest
import json
from common.logging_utils import log_json_event

def test_log_json_event(caplog):
    caplog.set_level("INFO")
    log_json_event("test_event", request_id="123", extra_field="value")
    
    # Check if JSON_EVENT was logged
    assert "JSON_EVENT:" in caplog.text
    
    # Extract JSON part
    json_str = caplog.text.split("JSON_EVENT: ")[1].strip()
    data = json.loads(json_str)
    
    assert data["event"] == "test_event"
    assert data["request_id"] == "123"
    assert data["extra_field"] == "value"

def test_log_json_event_no_request_id(caplog):
    caplog.set_level("INFO")
    log_json_event("event_only")
    
    json_str = caplog.text.split("JSON_EVENT: ")[1].strip()
    data = json.loads(json_str)
    
    assert data["event"] == "event_only"
    assert "request_id" not in data
