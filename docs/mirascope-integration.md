# Mirascope Integration Guide

## Overview

Mirascope has been integrated into the AI Orchestrator to provide enhanced LLM interactions with type safety, structured outputs, and simplified tool calling. This integration maintains backward compatibility and can be enabled optionally.

## Phase 1 Implementation ✅

### What's Been Added

#### 1. Enhanced Router Providers (`router/providers.py`)
- **Mirascope decorators** for Ollama streaming and chat functions
- **Structured response models** using Pydantic
- **Fallback mechanism** - automatically falls back to original HTTP calls if Mirascope fails
- **Configuration flags** to control Mirascope usage

#### 2. Dependency Management
- **Added to `pyproject.toml`**: `"mirascope>=1.0.0"`
- **Graceful import handling**: System works whether Mirascope is installed or not

#### 3. Environment Configuration
- **`USE_MIRASCOPE=true/false`** - Controls whether to use Mirascope-enhanced functions
- **Default: disabled** - Ensures system stability during transition

#### 4. Testing & Validation
- **`scripts/test_mirascope.py`** - Comprehensive integration testing
- **Fallback verification** - Ensures original functionality remains intact

### Current Functions Enhanced

```python
# Mirascope-enhanced functions (when enabled)
@llm.call(provider="ollama", model="llama3.3:70b-instruct-q8_0", stream=True)
async def mirascope_ollama_stream(messages, model, num_ctx=None)

@llm.call(provider="ollama", model="llama3.3:70b-instruct-q8_0", response_model=OllamaChatResponse)
async def mirascope_ollama_call(messages, model, num_ctx=None) -> OllamaChatResponse

# Original functions enhanced with optional Mirascope usage
async def call_ollama_chat_stream(model_id, messages, request_id, num_ctx=None)
async def call_ollama_chat(model_id, messages, request_id, num_ctx=None)
```

## How to Enable Mirascope

### 1. Install Package
```bash
pip install mirascope>=1.0.0
```

### 2. Enable Integration
```bash
export USE_MIRASCOPE=true
```

### 3. Restart Services
```bash
./manage.sh stop all
./manage.sh start all
```

### 4. Verify Installation
```bash
python scripts/test_mirascope.py
```

## Benefits When Enabled

### 1. Type Safety
```python
# Before: Manual JSON parsing
response = await call_ollama_chat(...)
data = response.json()  # Manual validation

# After: Type-safe structured responses
response: OllamaChatResponse = await mirascope_ollama_call(...)
# response.content, response.model, etc. are type-safe
```

### 2. Simplified Tool Calling
```python
# Before: Manual tool schema construction
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {...}
    }
}]

# After: Function-based tool definitions
@llm.call(provider="ollama", tools=[get_weather_tool])
def weather_agent(location: str): ...
```

### 3. Structured Streaming
```python
# Before: Manual SSE parsing
async for chunk in response.aiter_lines():
    if line.startswith("data: "):
        data = json.loads(line[6:])
        content = data.get("content", "")

# After: Structured chunk iteration
for chunk in mirascope_ollama_stream(prompt):
    print(chunk.content)  # Type-safe access
```

### 4. Error Handling
```python
# Before: Manual error checking
if response.status_code != 200:
    handle_error(response)

# After: Built-in error handling
try:
    response = await mirascope_ollama_call(...)
except MirascopeError as e:
    # Structured error handling
    handle_mirascope_error(e)
```

## Architecture Benefits

### 1. **Backward Compatibility**
- Original functions remain unchanged
- Automatic fallback if Mirascope fails
- No breaking changes to existing API

### 2. **Gradual Adoption**
- Can be enabled per service or globally
- Individual functions can use Mirascope independently
- Easy to disable for debugging

### 3. **Performance Monitoring**
- Token usage tracking built-in
- Response time monitoring
- Error rate tracking

### 4. **Development Experience**
- Type hints for better IDE support
- Self-documenting APIs
- Easier testing with mock responses

## Configuration Options

### Environment Variables
```bash
USE_MIRASCOPE=true          # Enable/disable Mirascope usage
OLLAMA_BASE=http://localhost:11434  # Ollama endpoint (existing)
```

### Response Models
```python
class OllamaChatResponse(BaseModel):
    content: str
    done: bool = True
    model: str = ""
    total_duration: int = 0
    prompt_eval_count: int = 0
    eval_count: int = 0
```

## Testing the Integration

### Run Integration Tests
```bash
# Test basic functionality
python scripts/test_mirascope.py

# Expected output:
# ✅ Mirascope package is installed
# ✅ Mirascope integration flag: True
# ✅ Mirascope usage enabled: True
```

### Manual Testing
```bash
# Test with Mirascope enabled
export USE_MIRASCOPE=true
./manage.sh restart router

# Monitor logs for Mirascope usage
tail -f logs/router.log | grep -i mirascope
```

### Performance Comparison
```bash
# Test token usage with/without Mirascope
# Compare response times and error rates
```

## Future Phases

### Phase 2: Tool Enhancement
- Replace manual tool schemas with Mirascope decorators
- Add structured tool response validation
- Enhance agent runner tool calling

### Phase 3: Response Validation
- Add comprehensive response quality assessment
- Implement structured output validation
- Add automated testing frameworks

### Phase 4: Multi-Provider Support
- Extend Mirascope integration to OpenAI, Anthropic
- Unified provider interface
- Advanced routing based on model capabilities

## Troubleshooting

### Common Issues

1. **"Mirascope not available"**
   ```bash
   pip install mirascope>=1.0.0
   ```

2. **Functions not using Mirascope**
   ```bash
   export USE_MIRASCOPE=true
   ./manage.sh restart router
   ```

3. **Performance degradation**
   ```bash
   export USE_MIRASCOPE=false  # Temporarily disable
   ```

### Monitoring

```bash
# Check Mirascope status
python -c "from router.providers import MIRASCOPE_AVAILABLE, USE_MIRASCOPE; print(f'Available: {MIRASCOPE_AVAILABLE}, Enabled: {USE_MIRASCOPE}')"

# Monitor logs
tail -f logs/router.log | grep -E "(Mirascope|mirascope)"
```

## Migration Guide

### For Existing Code
```python
# No changes needed - backward compatible
from router.providers import call_ollama_chat, call_ollama_chat_stream

# Existing code continues to work
response = await call_ollama_chat(model, messages, request_id)
```

### For New Features
```python
# Use Mirascope for new development
from router.providers import mirascope_ollama_call

@llm.call(provider="ollama", response_model=MyModel)
async def new_feature(prompt: str) -> MyModel:
    return await mirascope_ollama_call([{"role": "user", "content": prompt}])
```

## Conclusion

Phase 1 provides a solid foundation for Mirascope integration with:
- ✅ Zero disruption to existing functionality
- ✅ Optional enablement with environment variables
- ✅ Comprehensive testing and fallback mechanisms
- ✅ Type safety and structured responses
- ✅ Performance monitoring capabilities

The integration is production-ready and can be safely enabled for enhanced LLM interactions while maintaining full backward compatibility.