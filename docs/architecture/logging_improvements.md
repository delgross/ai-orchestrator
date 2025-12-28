# Logging, Error Handling, and Debugging Improvements

## Current State Analysis

### ✅ What's Good
- Basic logging infrastructure in place
- JSON_EVENT logging for structured events
- Error handling with try/except blocks
- Logs captured by launchd

### ❌ Issues Found

1. **No Request ID Tracking**
   - Can't trace a request through the system
   - Hard to correlate logs from same request
   - No way to debug specific user queries

2. **Hardcoded Log Level**
   - Set to INFO, no way to change via env var
   - Can't enable DEBUG logging when needed
   - No per-module log levels

3. **Inconsistent Error Logging**
   - Some errors logged at DEBUG level (might be missed)
   - Some exceptions caught but not logged
   - Error context sometimes missing

4. **No Structured Logging Context**
   - Can't add context to all logs in a request
   - Hard to filter logs by user/session
   - No correlation between related operations

5. **Limited Debugging Information**
   - No stack traces for non-critical errors
   - Missing timing information in some logs
   - No request/response logging for debugging

6. **No Log File Option**
   - Only stdout/stderr (though launchd captures it)
   - No separate error log file
   - No log rotation

## Recommended Improvements

### 1. Add Request ID Tracking (High Priority)

**Benefits:**
- Trace requests end-to-end
- Correlate logs from same request
- Debug specific user queries

**Implementation:**
```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default='')

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# In logging:
logger.info("message", extra={"request_id": request_id_var.get()})
```

### 2. Configurable Log Level (Medium Priority)

**Benefits:**
- Enable DEBUG when troubleshooting
- Reduce noise in production
- Per-module control

**Implementation:**
```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
```

### 3. Structured Logging Context (Medium Priority)

**Benefits:**
- Add context to all logs in a request
- Filter by user/session/model
- Better observability

**Implementation:**
```python
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get('')
        record.agent_model = get_agent_model()
        return True
```

### 4. Enhanced Error Logging (High Priority)

**Benefits:**
- Never miss important errors
- Full context for debugging
- Stack traces when needed

**Implementation:**
- Log all exceptions with full traceback
- Include request context in error logs
- Use appropriate log levels (ERROR for failures, WARNING for recoverable)

### 5. Request/Response Logging (Low Priority)

**Benefits:**
- Debug API interactions
- See what LLM receives/returns
- Troubleshoot tool calls

**Implementation:**
- Log request summaries (model, message count, tools)
- Log response summaries (choices, tool calls)
- Configurable verbosity

### 6. Log File Support (Low Priority)

**Benefits:**
- Separate error logs
- Log rotation
- Better organization

**Implementation:**
- Optional file handler
- Rotating file handler for size management
- Separate error log file

## Priority Implementation Order

1. **Request ID tracking** - Most valuable for debugging
2. **Configurable log level** - Easy win, high value
3. **Enhanced error logging** - Better error visibility
4. **Structured logging context** - Better observability
5. **Request/response logging** - Nice to have
6. **Log file support** - Nice to have

## Example Improved Logging

**Before:**
```
2025-01-17 16:31:05,795 ERROR agent_runner Agent loop failed
```

**After:**
```
2025-01-17 16:31:05,795 ERROR agent_runner [req-abc123] Agent loop failed: AttributeError: 'Analytics' object has no attribute 'observe_user_preference'
  model: openai:gpt-5-chat-latest
  step: 0
  tool_calls: []
  traceback: ...
```











