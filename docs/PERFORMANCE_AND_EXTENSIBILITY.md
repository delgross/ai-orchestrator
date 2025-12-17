# Performance Improvements & Extensibility Best Practices

## 🚀 Performance Improvements

### 1. **HTTP Connection Pooling Configuration** ⚡ HIGH IMPACT

**Current State:**
```python
self.client = httpx.AsyncClient(timeout=HTTP_TIMEOUT_S, trust_env=False)
```

**Issue:** No connection pool limits configured. Default limits may be too restrictive or too permissive.

**Fix:**
```python
self.client = httpx.AsyncClient(
    timeout=HTTP_TIMEOUT_S,
    trust_env=False,
    limits=httpx.Limits(
        max_keepalive_connections=20,  # Reuse connections
        max_connections=100,            # Max concurrent connections
        keepalive_expiry=30.0           # Keep connections alive for 30s
    ),
    http2=True  # Enable HTTP/2 for better performance (if supported)
)
```

**Impact:** 
- ✅ Reuses connections (faster subsequent requests)
- ✅ Better resource management
- ✅ 20-30% faster for multiple requests to same provider

---

### 2. **Response Caching for Chat Completions** 💾 MEDIUM IMPACT

**Current State:** Only models list is cached. Chat completions are never cached.

**Opportunity:** Cache non-streaming responses for identical requests (same model + messages).

**Implementation:**
```python
from functools import lru_cache
import hashlib

def _cache_key(model: str, messages: List[Dict], **params) -> str:
    """Generate cache key from request."""
    key_data = json.dumps({
        "model": model,
        "messages": messages,
        "params": sorted(params.items())
    }, sort_keys=True)
    return hashlib.sha256(key_data.encode()).hexdigest()

# In chat_completions endpoint:
if not stream:
    cache_key = _cache_key(model_id, body["messages"], 
                          temperature=body.get("temperature"))
    if cache_key in state.response_cache:
        return JSONResponse(content=state.response_cache[cache_key])
    
    # ... make request ...
    
    # Cache successful responses (TTL: 60s)
    if r.status_code == 200:
        state.response_cache[cache_key] = response_data
```

**Impact:**
- ✅ Faster responses for repeated queries
- ✅ Reduces API costs
- ⚠️ Only cache if `temperature=0` (deterministic) or user explicitly requests caching

---

### 3. **Parallel Provider Health Checks** ⚡ LOW-MEDIUM IMPACT

**Current State:** Health checks are sequential.

**Fix:**
```python
# In /health endpoint:
health_tasks = [
    _check_ollama(),
    _check_agent_runner(),
    *[_check_provider(p) for p in state.providers.values()]
]
results = await asyncio.gather(*health_tasks, return_exceptions=True)
```

**Impact:** Health check endpoint 3-5x faster with multiple providers.

---

### 4. **Lazy Provider Loading** 💾 LOW IMPACT

**Current State:** All providers loaded at startup.

**Opportunity:** Load providers on-demand or in background.

**Impact:** Faster startup time if many providers configured.

---

## 🏗️ Extensibility Best Practices

### 1. **Provider Plugin System** 🔌 CRITICAL FOR EXTENSIBILITY

**Current State:** Hardcoded provider types (`openai_compat`, `ollama`).

**Problem:** Adding new provider types requires modifying core router code.

**Solution: Provider Registry Pattern:**

```python
# router/providers/base.py
from abc import ABC, abstractmethod

class ProviderBase(ABC):
    """Base class for all providers."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
    
    @abstractmethod
    async def chat_completions(self, model: str, messages: List[Dict], **kwargs) -> Dict:
        """Make a chat completion request."""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[Dict]:
        """List available models."""
        pass

# router/providers/registry.py
PROVIDER_REGISTRY: Dict[str, Type[ProviderBase]] = {}

def register_provider(type_name: str, provider_class: Type[ProviderBase]):
    """Register a new provider type."""
    PROVIDER_REGISTRY[type_name] = provider_class

def create_provider(name: str, config: Dict) -> ProviderBase:
    """Create a provider instance from config."""
    ptype = config.get("type")
    if ptype not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider type: {ptype}")
    return PROVIDER_REGISTRY[ptype](name, config)

# router/providers/openai_compat.py
@register_provider("openai_compat")
class OpenAICompatProvider(ProviderBase):
    async def chat_completions(self, model: str, messages: List[Dict], **kwargs):
        # Implementation
        pass

# router/providers/ollama.py
@register_provider("ollama")
class OllamaProvider(ProviderBase):
    async def chat_completions(self, model: str, messages: List[Dict], **kwargs):
        # Implementation
        pass
```

**Benefits:**
- ✅ Add new providers without touching core router
- ✅ Clear separation of concerns
- ✅ Easy to test individual providers
- ✅ Can load providers from plugins/imports

---

### 2. **Middleware/Plugin System** 🔌 HIGH VALUE

**Current State:** Hardcoded middleware (RequestIDMiddleware).

**Solution: Middleware Chain:**

```python
# router/middleware/base.py
class Middleware(ABC):
    @abstractmethod
    async def process_request(self, request: Request) -> Optional[Response]:
        """Process request, return Response to short-circuit or None to continue."""
        pass
    
    @abstractmethod
    async def process_response(self, request: Request, response: Response) -> Response:
        """Process response before returning."""
        pass

# router/middleware/chain.py
class MiddlewareChain:
    def __init__(self):
        self.middlewares: List[Middleware] = []
    
    def add(self, middleware: Middleware):
        self.middlewares.append(middleware)
    
    async def process(self, request: Request, handler):
        # Process request
        for mw in self.middlewares:
            result = await mw.process_request(request)
            if result:
                return result
        
        # Call handler
        response = await handler(request)
        
        # Process response
        for mw in reversed(self.middlewares):
            response = await mw.process_response(request, response)
        
        return response
```

**Benefits:**
- ✅ Add auth, rate limiting, logging, etc. without modifying core
- ✅ Reusable middleware components
- ✅ Easy to enable/disable features

---

### 3. **Configuration Management** 📋 MEDIUM VALUE

**Current State:** Environment variables scattered throughout code.

**Solution: Configuration Class:**

```python
# router/config.py
from pydantic import BaseSettings, Field
from typing import Optional

class RouterConfig(BaseSettings):
    """Centralized configuration."""
    
    # Provider config
    providers_yaml: str = Field(default="~/ai/providers.yaml", env="PROVIDERS_YAML")
    ollama_base: str = Field(default="http://127.0.0.1:11434", env="OLLAMA_BASE")
    
    # Performance
    http_timeout_s: float = Field(default=120.0, env="HTTP_TIMEOUT_S")
    max_concurrency: int = Field(default=0, env="ROUTER_MAX_CONCURRENCY")
    models_cache_ttl_s: float = Field(default=600.0, env="MODELS_CACHE_TTL_S")
    
    # Security
    auth_token: Optional[str] = Field(default=None, env="ROUTER_AUTH_TOKEN")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

config = RouterConfig()
```

**Benefits:**
- ✅ Type-safe configuration
- ✅ Validation on startup
- ✅ Single source of truth
- ✅ Easy to document defaults

---

### 4. **Error Handling Strategy** 🛡️ MEDIUM VALUE

**Current State:** Inconsistent error handling.

**Solution: Error Hierarchy:**

```python
# router/errors.py
class RouterError(Exception):
    """Base exception for router errors."""
    pass

class ProviderError(RouterError):
    """Provider-specific error."""
    def __init__(self, provider: str, message: str, status_code: int = 500):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message)

class ModelNotFoundError(ProviderError):
    """Model not found error."""
    pass

# In router:
try:
    result = await provider.chat_completions(...)
except ModelNotFoundError as e:
    raise HTTPException(status_code=404, detail={
        "error": "Model not found",
        "model": e.model,
        "provider": e.provider
    })
except ProviderError as e:
    raise HTTPException(status_code=e.status_code, detail={
        "error": str(e),
        "provider": e.provider
    })
```

**Benefits:**
- ✅ Consistent error handling
- ✅ Better error messages
- ✅ Easier debugging
- ✅ Can add retry logic per error type

---

### 5. **Code Organization** 📁 HIGH VALUE

**Current State:** Single 800-line file.

**Recommended Structure:**
```
router/
├── __init__.py
├── main.py              # FastAPI app setup
├── config.py            # Configuration
├── state.py             # Application state
├── errors.py            # Error classes
├── middleware/
│   ├── __init__.py
│   ├── base.py
│   ├── request_id.py
│   └── chain.py
├── providers/
│   ├── __init__.py
│   ├── base.py
│   ├── registry.py
│   ├── openai_compat.py
│   └── ollama.py
├── routes/
│   ├── __init__.py
│   ├── health.py
│   ├── models.py
│   └── chat.py
└── utils/
    ├── __init__.py
    ├── http.py
    └── cache.py
```

**Benefits:**
- ✅ Easier to navigate
- ✅ Better testability
- ✅ Clear separation of concerns
- ✅ Easier to extend

---

### 6. **Type Safety & Validation** 🔒 MEDIUM VALUE

**Current State:** Using dataclasses, but minimal validation.

**Solution: Use Pydantic:**

```python
from pydantic import BaseModel, Field, validator

class ProviderConfig(BaseModel):
    name: str
    type: str = Field(..., regex="^(openai_compat|ollama)$")
    base_url: str
    api_key_env: Optional[str] = None
    default_headers: Optional[Dict[str, str]] = None
    
    @validator("base_url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")
```

**Benefits:**
- ✅ Automatic validation
- ✅ Better IDE support
- ✅ Self-documenting
- ✅ Type checking at runtime

---

## 🎯 Priority Recommendations

### Immediate (High Impact, Low Effort):
1. ✅ **HTTP Connection Pooling** - 20-30% performance improvement
2. ✅ **Provider Plugin System** - Critical for future extensibility
3. ✅ **Code Organization** - Makes everything easier

### Short-term (Medium Impact):
4. **Response Caching** - Reduces API costs
5. **Configuration Class** - Better maintainability
6. **Error Hierarchy** - Better debugging

### Long-term (Nice to Have):
7. **Middleware System** - Advanced features
8. **Lazy Loading** - Faster startup
9. **Pydantic Models** - Type safety

---

## 📝 Implementation Notes

- **Start with connection pooling** - Biggest performance win
- **Refactor incrementally** - Don't rewrite everything at once
- **Keep backward compatibility** - Existing code should still work
- **Add tests** - Especially for provider plugins
- **Document extension points** - Make it easy for others to extend

