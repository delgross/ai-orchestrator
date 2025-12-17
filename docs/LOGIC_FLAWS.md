# Logic Flaws Found in Router Code

## Critical Issues

### 1. **Concurrency Control Scope Bug** ⚠️ CRITICAL
**Location:** Lines 667-744

**Problem:** The semaphore (concurrency limit) only protects agent and RAG requests, but ALL provider routing (Ollama, OpenAI-compat) is OUTSIDE the `async with lock_ctx:` block.

**Impact:** 
- Concurrency limit is completely bypassed for provider requests
- If `ROUTER_MAX_CONCURRENCY=5`, you could still have 100+ concurrent provider requests
- Defeats the purpose of rate limiting

**Current Code:**
```python
async with lock_ctx:  # Only protects agent/rag
    if prefix == "agent":
        ...
    if prefix == "rag":
        ...

# Provider routing is OUTSIDE the lock!
prov = state.providers.get(prefix)
if prov.ptype == "ollama":
    ...
```

**Fix:** Move all provider routing inside the `async with lock_ctx:` block.

---

### 2. **Duplicate Ollama Models in /v1/models**
**Location:** Lines 625-631

**Problem:** If `OLLAMA_BASE` matches an Ollama provider's `base_url`, models are fetched twice and appear duplicated.

**Example:**
- `OLLAMA_BASE = "http://127.0.0.1:11434"`
- Provider `ollama` has `base_url = "http://127.0.0.1:11434"`
- Both `_fetch_ollama_models()` and `_fetch_ollama_models(prov.base_url)` fetch the same models

**Fix:** Track fetched URLs and skip duplicates, or remove hardcoded `OLLAMA_BASE` fetch if an Ollama provider exists.

---

### 3. **Missing JSON Parsing Error Handling**
**Location:** Line 331 in `_call_ollama_chat()`

**Problem:** `r.json()` can raise `json.JSONDecodeError` if Ollama returns invalid JSON, which will crash the request.

**Current Code:**
```python
j = r.json()  # Can raise JSONDecodeError
```

**Fix:** Wrap in try/except and handle gracefully.

---

### 4. **Empty model_id Not Validated**
**Location:** After `_parse_model()` call

**Problem:** If user passes `"provider:"` (empty model name), `model_id` will be empty string `""`, which should be rejected.

**Current Code:**
```python
prefix, model_id = _parse_model(body.get("model"))
# No validation that model_id is not empty
```

**Fix:** Validate `model_id` is not empty after parsing.

---

### 5. **Health Check Logic Flaw**
**Location:** Line 550

**Problem:** Health check requires `len(state.providers) > 0`, so if no providers are configured, it will always show "degraded" even if router is working fine.

**Current Code:**
```python
overall_ok = ollama_ok and agent_ok and len(state.providers) > 0
```

**Fix:** Health check should be based on router functionality, not provider count. Providers can be optional.

---

### 6. **Race Condition in Models Cache**
**Location:** Line 645

**Problem:** `state.models_cache = (now, payload)` is not thread-safe. Multiple concurrent requests could:
1. Both check cache (miss)
2. Both fetch models
3. Both update cache (last write wins, but wasted work)

**Fix:** Use a lock or check cache again after acquiring lock.

---

## Medium Priority Issues

### 7. **Inconsistent Error Handling**
Some functions return empty lists on error (`_fetch_ollama_models`, `_fetch_openai_models`), others raise exceptions. This makes error handling inconsistent.

### 8. **Missing Request ID in Some Error Logs**
Some error logs don't include `request_id`, making debugging harder.

---

## Recommendations

1. **Fix concurrency control immediately** - This is a critical bug that defeats rate limiting
2. **Add JSON parsing error handling** - Prevents crashes on malformed responses
3. **Validate model_id** - Prevents invalid requests
4. **Fix duplicate models** - Improves user experience
5. **Fix health check logic** - More accurate status reporting
6. **Add cache locking** - Prevents wasted work (nice to have)

