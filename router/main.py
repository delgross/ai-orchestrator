from __future__ import annotations
import asyncio
import json
import os
import time
from typing import Any, Dict
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import shutil

from common.logging_setup import setup_logger
from common.unified_tracking import track_event, EventCategory, EventSeverity
from common.constants import (
    PREFIX_AGENT, PREFIX_OLLAMA, PREFIX_RAG,
    OBJ_MODEL, OBJ_LIST,
    MODEL_AGENT_MCP, MODEL_ROUTER
)

from router.config import state, VERSION, OLLAMA_BASE, AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH, MODELS_CACHE_TTL_S, MAX_REQUEST_BODY_BYTES, FS_ROOT, RAG_BASE
from router.utils import join_url, sanitize_messages, parse_model_string
from router.middleware import require_auth
from router.providers import load_providers, call_ollama_chat, provider_headers
from router.rag import call_rag
from router.agent_manager import check_agent_runner_health, get_agent_models
from router.admin import router as admin_router
from common.observability import ComponentType, get_observability
from common.observability_middleware import ObservabilityMiddleware
from common.anomaly_detection_task import run_anomaly_detection

# Concurrency limiting
semaphore = None
if state.max_concurrency > 0:
    semaphore = asyncio.Semaphore(state.max_concurrency)

logger = setup_logger("router")

@asynccontextmanager
async def log_time(operation_name: str, level=logging.DEBUG):
    t0 = time.time()
    try:
        yield
    finally:
        duration = time.time() - t0
        logger.log(level, f"PERF: {operation_name} completed in {duration:.4f}s")

async def run_environment_watchdog():
    """Continuously check critical dependencies."""
    logger.info("🛡️ Starting Environment Watchdog...")
    
    while True:
        try:
            # 1. Check Ollama
            try:
                r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=1.0)
                if r.status_code == 200: 
                    # Only log if it was previously broken to avoid spam, or debug level
                    # state.circuit_breakers.record_success("ollama") # Circuit breaker handles this
                    pass
                else: 
                    logger.warning(f"⚠️ Watchdog: Ollama returned {r.status_code}")
            except Exception as e:
                logger.error(f"❌ Watchdog: Ollama is OFFLINE: {e}")
                # We could actively attempt to restart it here if we had permissions

            # 2. Check Agent Runner
            try:
                r = await state.client.get(f"{AGENT_RUNNER_URL}/health", timeout=1.0)
                if r.status_code != 200:
                    logger.warning(f"⚠️ Watchdog: Agent Runner returned {r.status_code}")
            except Exception:
                pass # Agent runner offline, logged elsewhere or just retry

            # 3. Check RAG Server
            try:
                r = await state.client.get(f"{RAG_BASE}/health", timeout=1.0)
                if r.status_code != 200:
                    logger.warning(f"⚠️ Watchdog: RAG Server returned {r.status_code}")
                # else: state.circuit_breakers.record_success("rag")
            except Exception as e:
                logger.error(f"❌ Watchdog: RAG Server is OFFLINE: {e}")

        except Exception as e:
            logger.error(f"Watchdog crash: {e}")
        
        await asyncio.sleep(60) # Run every minute

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting Router v{VERSION}")
    track_event("router_startup", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, message=f"Router version {VERSION} starting up")
    setup_logger("common.circuit_breaker", log_file="router.log")
    state.providers = load_providers()
    
    # Start Background Tasks
    env_task = asyncio.create_task(run_environment_watchdog())
    anomaly_task = asyncio.create_task(run_anomaly_detection(check_interval=60.0))
    
    yield
    # Shutdown
    track_event("router_shutdown", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, message="Router is shutting down")
    
    env_task.cancel()
    anomaly_task.cancel()
    try:
        await env_task
        await anomaly_task
    except asyncio.CancelledError:
        pass
    await state.client.aclose()
    # Close observability client if it exists
    obs = get_observability()
    # Note: client closure is handled in config state usually, but obs has its own if used

app = FastAPI(title="router", version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    ObservabilityMiddleware,
    component_type=ComponentType.ROUTER,
    component_id="router-main"
)

# Mount static files
dashboard_v2_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "v2")
if os.path.exists(dashboard_v2_path):
    app.mount("/v2", StaticFiles(directory=dashboard_v2_path), name="dashboard_v2")

app.include_router(admin_router)

@app.get("/")
async def root(request: Request):
    # Return JSON health info when client explicitly requests JSON
    accept = request.headers.get("accept", "")
    if "application/json" in accept.lower():
        return {"ok": True, "version": VERSION}
    # Default: redirect to dashboard UI
    return RedirectResponse(url="/v2/index.html")

@app.get("/dashboard")
async def dashboard_redirect():
    """Redirect /dashboard to the UI index page."""
    return RedirectResponse(url="/v2/index.html")

@app.get("/sw.js")
async def service_worker_killer():
    """Serve a self-destructing Service Worker."""
    content = """
    self.addEventListener('install', function(e) {
        self.skipWaiting();
    });
    self.addEventListener('activate', function(e) {
        self.registration.unregister()
            .then(function() { return self.clients.matchAll(); })
            .then(function(clients) {
                clients.forEach(client => client.navigate(client.url));
            });
    });
    """
    return HTMLResponse(content, media_type="application/javascript")

@app.get("/health")
async def health(request: Request):
    ollama_ok = False
    try:
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=2.0)
        ollama_ok = r.status_code < 400
    except Exception:
        pass
    
    agent_ok = await check_agent_runner_health()
    overall_ok = ollama_ok and agent_ok
    
    return {
        "status": "healthy" if overall_ok else "degraded",
        "ok": overall_ok,
        "services": {
            "router": {"ok": True, "version": VERSION},
            "ollama": {"ok": ollama_ok},
            "agent_runner": {"ok": agent_ok},
        }
    }

@app.get("/v1/models")
async def v1_models(request: Request):
    require_auth(request)
    # Cache logic
    ts, cached = state.models_cache
    if cached and (time.time() - ts) < MODELS_CACHE_TTL_S:
        state.cache_hits += 1
        return cached
    
    state.cache_misses += 1
    data = []
    
    now = int(time.time())
    
    # Helper for compliant structure
    def make_model(mid, owner):
        return {
            "id": mid, 
            "object": OBJ_MODEL, 
            "created": now, 
            "owned_by": owner,
            "permission": [],
            "root": mid,
            "parent": None
        }

    # 1. Base models
    data.append(make_model(MODEL_AGENT_MCP, "agent_runner"))
    data.append(make_model(MODEL_ROUTER, "router"))
    
    # 2. Agent Runner models
    agent_models = await get_agent_models()
    for m in agent_models:
        m_id = m.get("id", "")
        if not m_id.startswith(f"{PREFIX_AGENT}:"):
            m["id"] = f"{PREFIX_AGENT}:{m_id}"
        data.append(m)
        
    # 3. Ollama models
    try:
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=3.0)
        if r.status_code == 200:
            for m in r.json().get("models", []):
                name = m.get("name", "")
                data.append({"id": f"{PREFIX_OLLAMA}:{name}", "object": OBJ_MODEL, "owned_by": "ollama"})
    except Exception:
        pass

    # 4. Providers
    for p_name, prov in state.providers.items():
        try:
            url = join_url(prov.base_url, prov.models_path)
            r = await state.client.get(url, headers=provider_headers(prov), timeout=3.0)
            if r.status_code == 200:
                p_models = r.json().get("data", [])
                for m in p_models:
                    m_id = m.get("id", "")
                    data.append({"id": f"{p_name}:{m_id}", "object": OBJ_MODEL, "owned_by": p_name})
        except Exception:
            pass
    
    payload = {"object": OBJ_LIST, "data": data}
    state.models_cache = (time.time(), payload)
    return payload

@app.post("/v1/embeddings")
async def embeddings(request: Request):
    require_auth(request)
    
    # Check body size
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Request body too large")

    body = await request.json()
    model = body.get("model", "")
    logger.debug(f"ROUTER Received Model: {model}")
    prefix, model_id = parse_model_string(model, default_prefix="")
    
    # 0. Default / Fallback Handling
    # If no prefix is provided (e.g. "text-embedding-ada-002"), or if specifically asking for "default"
    # we alias it to the system default embedding model.
    if not prefix or model == "default":
        logger.info(f"Using default embedding model '{state.default_embedding_model}' for request '{model}'")
        model = state.default_embedding_model
        prefix, model_id = parse_model_string(model)
        logger.debug(f"Parsed Prefix: {prefix}, ID: {model_id}")
    
    # Update body to use the stripped model ID
    body["model"] = model_id

    # 1. Ollama (Explicit or Default if no prefix)
    # Note: We default to Ollama if no prefix is found, assuming local execution
    if prefix == PREFIX_OLLAMA or not prefix:
        url = join_url(OLLAMA_BASE, "/v1/embeddings")
        try:
            r = await state.client.post(url, json=body)
            if r.status_code >= 400:
                # If Ollama 404s, implies model not found. We could fall through? 
                # But safer to just report error.
                raise HTTPException(status_code=r.status_code, detail=r.text)
            return JSONResponse(r.json())
        except Exception as e:
            # If explicit ollama prefix, fail hard. If implicit, maybe we could try providers? 
            # But let's keep it simple.
            logger.error(f"Ollama embedding failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    # 2. Providers
    prov = state.providers.get(prefix)
    if prov:
        if not state.circuit_breakers.is_allowed(prefix):
            raise HTTPException(status_code=503, detail=f"Provider '{prefix}' is currently disabled")

        url = join_url(prov.base_url, prov.embeddings_path)
        try:
            # Note: Provider might expect input, Ollama v1 also expects input.
            r = await state.client.post(url, headers=provider_headers(prov), json=body)
            if r.status_code >= 400:
                state.circuit_breakers.record_failure(prefix)
                raise HTTPException(status_code=r.status_code, detail=r.text)
            state.circuit_breakers.record_success(prefix)
            return JSONResponse(r.json())
        except Exception as e:
            state.circuit_breakers.record_failure(prefix)
            logger.error(f"Provider {prefix} embedding failed: {e}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))
            
    raise HTTPException(status_code=404, detail=f"Provider not found for embedding model: {model}")



# --- Audio API ---

@app.post("/v1/audio/transcriptions")
async def audio_transcriptions(request: Request):
    """Proxy audio transcriptions to OpenAI provider."""
    require_auth(request)
    
    # 1. Identify OpenAI Provider
    prov = state.providers.get("openai")
    if not prov:
        # Try finding one
        for p_name, p in state.providers.items():
            if "openai.com" in p.base_url:
                prov = p
                break
    
    if not prov:
        raise HTTPException(status_code=503, detail="No OpenAI provider configured for audio")
        
    url = join_url(prov.base_url, "/audio/transcriptions")
    
    # 2. Proxy Multipart Request
    # We must read the form data and reconstruct it or stream it.
    # Streaming multipart is hard. Simplified approach: Read all, then post.
    # Limit body size for safety.
    
    try:
        form = await request.form()
        
        # httpx needs a specific files/data structure
        files = []
        data = {}
        
        for field_name, value in form.items():
            if isinstance(value, UploadFile):
                # It's a file
                content = await value.read()
                files.append((field_name, (value.filename, content, value.content_type)))
            else:
                # It's a form field
                data[field_name] = value
                
        # 3. Call Upstream
        async with state.client.stream("POST", url, headers=provider_headers(prov), data=data, files=files, timeout=60.0) as r:
            body = await r.aread()
            return JSONResponse(json.loads(body), status_code=r.status_code)
            
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- OpenAI Files API ---

@app.post("/v1/files")
async def upload_file(request: Request, file: UploadFile = File(...), purpose: str = Form(...)):
    """Upload a file to the agent's sandbox (OpenAI Compatible)."""
    require_auth(request)
    
    upload_dir = os.path.join(FS_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = f"file-{uuid.uuid4().hex[:12]}"
    # Sanitize filename
    orig_name = file.filename or "unknown"
    safe_name = "".join([c for c in orig_name if c.isalnum() or c in "._-"]).strip()
    stored_name = f"{file_id}_{safe_name}"
    stored_path = os.path.join(upload_dir, stored_name)
    
    try:
        with open(stored_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(stored_path)
        
        logger.info(f"📁 File uploaded: {file.filename} -> {stored_path} ({file_size} bytes)")
        track_event("file_uploaded", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, 
                    message=f"File uploaded: {file.filename}", metadata={"file_id": file_id, "size": file_size})
        
        return {
            "id": file_id,
            "object": "file",
            "bytes": file_size,
            "created_at": int(time.time()),
            "filename": file.filename,
            "purpose": purpose,
            "status": "processed",
            "path": stored_path # Custom: help the agent find it
        }
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/v1/files")
async def list_files(request: Request):
    """List uploaded files."""
    require_auth(request)
    upload_dir = os.path.join(FS_ROOT, "uploads")
    if not os.path.exists(upload_dir):
        return {"object": "list", "data": []}
        
    data = []
    for f in os.listdir(upload_dir):
        if f.startswith("file-") and "_" in f:
            path = os.path.join(upload_dir, f)
            stat = os.stat(path)
            f_id, name = f.split("_", 1)
            data.append({
                "id": f_id,
                "object": "file",
                "bytes": stat.st_size,
                "created_at": int(stat.st_mtime),
                "filename": name,
                "purpose": "assistants",
                "status": "processed"
            })
            
    return {"object": "list", "data": data}

@app.get("/v1/files/{file_id}")
async def retrieve_file(file_id: str, request: Request):
    """Retrieve metadata for a file."""
    require_auth(request)
    upload_dir = os.path.join(FS_ROOT, "uploads")
    for f in os.listdir(upload_dir):
        if f.startswith(file_id):
            path = os.path.join(upload_dir, f)
            stat = os.stat(path)
            _, name = f.split("_", 1)
            return {
                "id": file_id,
                "object": "file",
                "bytes": stat.st_size,
                "created_at": int(stat.st_mtime),
                "filename": name,
                "purpose": "assistants",
                "status": "processed"
            }
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/v1/files/{file_id}/content")
async def retrieve_file_content(file_id: str, request: Request):
    """Retrieve the actual content of a file."""
    require_auth(request)
    upload_dir = os.path.join(FS_ROOT, "uploads")
    for f in os.listdir(upload_dir):
        if f.startswith(file_id):
            return FileResponse(os.path.join(upload_dir, f))
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    require_auth(request)
    
    # Check body size
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Request body too large")

    body = await request.json()
    model = body.get("model", "")
    request_id = request.state.request_id
    
    logger.info(f"REQ [{request_id}] Chat Completion: Model='{model}'")
    
    if not model or model == "agent" or " " in model: 
        logger.warning(f"REQ [{request_id}] Invalid/Unknown model '{model}', defaulting to {MODEL_AGENT_MCP}")
        model = MODEL_AGENT_MCP
    
    # Resolve alias
    if model == MODEL_ROUTER:
        model = state.system_router_model
        
    prefix, model_id = parse_model_string(model)
    logger.debug(f"REQ [{request_id}] Parsed Target: Prefix='{prefix}', ID='{model_id}'")
    
    msgs = body.get("messages", [])
    body["messages"] = sanitize_messages(msgs)
    
    # Concurrency limit
    async with log_time(f"Chat Request [{request_id}]", level=logging.INFO):
        if semaphore:
            async with semaphore:
                return await _handle_chat(request, body, prefix, model_id)
        else:
            return await _handle_chat(request, body, prefix, model_id)

async def _handle_chat(request: Request, body: Dict[str, Any], prefix: str, model_id: str):
    request_id = request.state.request_id

    if prefix == PREFIX_AGENT:
        # Route to agent runner
        url = join_url(AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH)
        
        # Check if streaming is requested
        if body.get("stream"):
            async def stream_wrapper():
                try:
                    # Create request task
                    task = asyncio.create_task(state.client.post(url, json=body, timeout=300.0))
                    
                    # Wait for task to complete, sending keep-alives
                    while not task.done():
                        yield ": keep-alive\n\n"
                        await asyncio.sleep(2.0)
                    
                    # Get result
                    r = await task
                    
                    if r.status_code != 200:
                        err_msg = r.text
                        try:
                            # Try to parse if it's already JSON
                            err_json = r.json()
                            if "detail" in err_json:
                                err_msg = err_json["detail"]
                            elif "error" in err_json:
                                err_msg = err_json["error"]
                        except Exception:
                            pass
                        
                        error_obj = {"error": {"message": err_msg, "type": "agent_runner_error", "code": r.status_code}}
                        yield f"data: {json.dumps(error_obj)}\n\n"
                        yield "data: [DONE]\n\n"
                        return

                    if r.status_code >= 500:
                        err_msg = "Agent Runner Unavailable (Warming Up / Building)"
                        logger.warning(f"Agent stream failed: {r.status_code}")
                        error_obj = {"error": {"message": err_msg, "type": "service_unavailable", "code": 503}}
                        yield f"data: {json.dumps(error_obj)}\n\n"
                        yield "data: [DONE]\n\n"
                        return

                    data = r.json()
                    content = data["choices"][0]["message"]["content"] or ""
                    usage = data.get("usage")
                    
                    base_chunk = {
                        "id": data.get("id"),
                        "object": "chat.completion.chunk",
                        "created": data.get("created"),
                        "model": data.get("model"),
                        "choices": [{"index": 0, "delta": {}, "finish_reason": None}]
                    }
                    
                    # 1. Yield Role
                    role_chunk = base_chunk.copy()
                    role_chunk["choices"] = [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
                    yield f"data: {json.dumps(role_chunk)}\n\n"
                    
                    # 2. Yield Content Chunks (Simulate Stream)
                    chunk_size = 20 # chars
                    for i in range(0, len(content), chunk_size):
                        segment = content[i:i+chunk_size]
                        delta_chunk = base_chunk.copy()
                        delta_chunk["choices"] = [{"index": 0, "delta": {"content": segment}, "finish_reason": None}]
                        yield f"data: {json.dumps(delta_chunk)}\n\n"
                        # Tiny sleep to allow client UI to update (prevent jank on huge messages)
                        await asyncio.sleep(0.01)

                    # 3. Yield Finish Reason & Usage
                    # OpenAI sends usage in a separate chunk usually, or with the final chunk
                    final_chunk = base_chunk.copy()
                    final_chunk["choices"] = [{"index": 0, "delta": {}, "finish_reason": data["choices"][0]["finish_reason"]}]
                    if usage:
                        final_chunk["usage"] = usage
                    
                    yield f"data: {json.dumps(final_chunk)}\n\n"
                    yield "data: [DONE]\n\n"

                except Exception as e:
                    logger.error(f"Agent request failed: {e}")
                    error_obj = {"error": {"message": str(e), "type": "internal_server_error"}}
                    yield f"data: {json.dumps(error_obj)}\n\n"
                    yield "data: [DONE]\n\n"

            return StreamingResponse(stream_wrapper(), media_type="text/event-stream")
        else:
            # Standard JSON proxy
            try:
                r = await state.client.post(url, json=body, timeout=300.0)
                if r.status_code >= 500:
                   logger.warning(f"Agent Runner returned {r.status_code}. Returning 503 to client.")
                   return JSONResponse({"error": {"message": "Agent Runner Unavailable (Warming Up / Building)", "type": "service_unavailable", "code": 503}}, status_code=503)
                return JSONResponse(r.json(), status_code=r.status_code)
            except Exception as e:
                logger.error(f"Agent request failed (non-streaming): {e}")
                raise HTTPException(status_code=502, detail=f"Agent Runner Unavailable: {str(e)}")
    
    elif prefix == PREFIX_OLLAMA:
        res = await call_ollama_chat(model_id, body["messages"], request_id)
        return JSONResponse(res)
        
    elif prefix == PREFIX_RAG:
        res = await call_rag(model_id, body)
        return JSONResponse(res)
    
    else:
        # Try finding in providers
        prov = state.providers.get(prefix)
        if prov:
            if not state.circuit_breakers.is_allowed(prefix):
                raise HTTPException(status_code=503, detail=f"Provider '{prefix}' is currently disabled via circuit breaker")

            state.provider_requests[prefix] = state.provider_requests.get(prefix, 0) + 1
            
            # BUDGET CHECK
            from common.budget import get_budget_tracker
            budget = get_budget_tracker()
            if not budget.check_budget():
                raise HTTPException(status_code=429, detail="Daily Budget Exceeded (Antigravity Cost Control)")

            url = join_url(prov.base_url, prov.chat_path)
            
            # Update body with the provider-specific model ID
            body["model"] = model_id
            
            # Check if streaming is requested
            if body.get("stream", False):
                # Passthrough with error tracking
                async def stream_gen():
                    try:
                        # Increased timeout to 120s for serverless cold boots (H100s)
                        async with state.client.stream("POST", url, headers=provider_headers(prov), json=body, timeout=120.0) as r:
                            if r.status_code >= 400:
                                state.circuit_breakers.record_failure(prefix)
                            else:
                                state.circuit_breakers.record_success(prefix)
                            
                            async for chunk in r.aiter_bytes():
                                yield chunk
                                # Try to sniff usage from chunk if possible? 
                                # Hard with raw bytes pass-through. 
                                # We'll estimate cost on input (pre-flight) for now to be safe?
                                # No, let's just not block functionality. Budget check happens at start.
                                
                        # Post-flight recording is hard in passthrough. 
                        # We will rely on Pre-Check mostly.
                    except Exception as e:
                        state.circuit_breakers.record_failure(prefix)
                        logger.error(f"Provider {prefix} call failed: {e}")
                        raise
                return StreamingResponse(stream_gen(), media_type="text/event-stream")
            else:
                # Regular non-streaming request
                try:
                    # Increased timeout to 120s for serverless cold boots (H100s)
                    r = await state.client.post(url, headers=provider_headers(prov), json=body, timeout=120.0)
                    if r.status_code >= 400:
                        state.circuit_breakers.record_failure(prefix)
                        raise HTTPException(status_code=r.status_code, detail=r.text)
                    
                    state.circuit_breakers.record_success(prefix)
                    data = r.json()
                    
                    # BUDGET RECORDING
                    try:
                        usage = data.get("usage", {})
                        in_tok = usage.get("prompt_tokens", 0)
                        out_tok = usage.get("completion_tokens", 0)
                        cost = budget.estimate_cost(body.get("model", ""), in_tok, out_tok)
                        if cost > 0:
                            budget.record_usage(prefix, cost)
                    except Exception:
                        pass
                    
                    return JSONResponse(data)
                except Exception as e:
                    state.circuit_breakers.record_failure(prefix)
                    logger.error(f"Provider {prefix} non-streaming call failed: {e}")
                    if isinstance(e, HTTPException):
                        raise
                    raise HTTPException(status_code=500, detail=str(e))
            
    raise HTTPException(status_code=404, detail=f"Provider or model not found: {prefix}:{model_id}")



@app.get("/stats")
async def stats(request: Request):
    require_auth(request)
    return {
        "uptime_s": round(time.time() - state.started_at, 2),
        "requests": state.request_count,
        "errors": state.error_count,
        "avg_response_time_ms": round(state.total_response_time_ms / max(1, state.request_count), 2),
        "cache": {
            "hits": state.cache_hits,
            "misses": state.cache_misses
        },
        "providers": state.provider_requests,
        "status_codes": state.request_by_status
    }
