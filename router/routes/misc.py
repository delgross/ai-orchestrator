import time
import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from router.config import state, VERSION, OLLAMA_BASE
from router.agent_manager import check_agent_runner_health
from router.routes.chat import check_streaming_health
from router.middleware import require_auth

router = APIRouter()
logger = logging.getLogger("router.misc")

@router.get("/")
async def root(request: Request):
    """Root endpoint returning service status."""
    return {"ok": True, "version": VERSION, "service": "Antigravity Router"}

@router.get("/prompt-inspector")
async def prompt_inspector(request: Request):
    """Serve the prompt inspection and editing interface."""
    require_auth(request)

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Prompt Inspector</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .form-group { margin: 10px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 3px; }
            textarea { height: 200px; font-family: monospace; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            .result { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px; white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto; }
            .error { background: #f8d7da; color: #721c24; }
            .success { background: #d4edda; color: #155724; }
            .tabs { display: flex; margin-bottom: 20px; }
            .tab { padding: 10px 20px; background: #e9ecef; border: none; cursor: pointer; }
            .tab.active { background: #007bff; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Prompt Inspector & Editor</h1>
            <p>Inspect system prompts, analyze query classification, and evaluate response quality.</p>

            <div class="tabs">
                <button class="tab active" onclick="showTab('inspect')">Prompt Inspector</button>
                <button class="tab" onclick="showTab('analyze')">Query Analyzer</button>
                <button class="tab" onclick="showTab('evaluate')">Response Evaluator</button>
            </div>

            <div id="inspect" class="tab-content active">
                <h2>🔍 Prompt Inspector</h2>
                <div class="form-group">
                    <label for="inspect-query">Query (optional):</label>
                    <input type="text" id="inspect-query" placeholder="Enter a sample query to see how it's analyzed">
                </div>
                <div class="form-group">
                    <label for="inspect-type">Override Query Type:</label>
                    <select id="inspect-type">
                        <option value="generic">Auto-detect</option>
                        <option value="simple">Simple</option>
                        <option value="technical">Technical</option>
                        <option value="system">System</option>
                    </select>
                </div>
                <button onclick="inspectPrompt()">Inspect Prompt</button>
                <div id="inspect-result" class="result"></div>
            </div>

            <div id="analyze" class="tab-content">
                <h2>🔎 Query Analyzer</h2>
                <div class="form-group">
                    <label for="analyze-query">Query to Analyze:</label>
                    <input type="text" id="analyze-query" placeholder="Enter query to analyze classification">
                </div>
                <button onclick="analyzeQuery()">Analyze Query</button>
                <div id="analyze-result" class="result"></div>
            </div>

            <div id="evaluate" class="tab-content">
                <h2>📊 Response Evaluator</h2>
                <div class="form-group">
                    <label for="eval-query">Original Query:</label>
                    <input type="text" id="eval-query" placeholder="The user's original question">
                </div>
                <div class="form-group">
                    <label for="eval-response">AI Response:</label>
                    <textarea id="eval-response" placeholder="Paste the AI response here"></textarea>
                </div>
                <div class="form-group">
                    <label for="eval-quality">Expected Quality:</label>
                    <select id="eval-quality">
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>
                <button onclick="evaluateResponse()">Evaluate Response</button>
                <div id="evaluate-result" class="result"></div>
            </div>
        </div>

        <script>
            function showTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }

            async function inspectPrompt() {
                const query = document.getElementById('inspect-query').value;
                const queryType = document.getElementById('inspect-type').value;
                const resultDiv = document.getElementById('inspect-result');

                resultDiv.textContent = 'Inspecting prompt...';
                resultDiv.className = 'result';

                try {
                    const response = await fetch('/admin/prompt/inspect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query, query_type: queryType })
                    });

                    const result = await response.json();

                    if (result.ok && result.result && result.result.ok && result.result.result && result.result.result.ok) {
                        const data = result.result.result;
                        resultDiv.className = 'result success';
                        resultDiv.textContent = JSON.stringify({
                            query_analysis: data.query_analysis,
                            prompt_details: {
                                estimated_tokens: data.prompt_details?.estimated_tokens || 'N/A',
                                character_count: data.prompt_details?.character_count || 'N/A'
                            },
                            full_prompt: data.prompt_details?.full_prompt || 'N/A',
                            components: data.components
                        }, null, 2);
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = 'Error: ' + (result.error || result.result?.error || result.result?.result?.error || 'Unknown error');
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = 'Error: ' + error.message;
                }
            }

            async function analyzeQuery() {
                const query = document.getElementById('analyze-query').value;
                const resultDiv = document.getElementById('analyze-result');

                resultDiv.textContent = 'Analyzing query...';
                resultDiv.className = 'result';

                try {
                    const response = await fetch('/admin/query/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });

                    const result = await response.json();

                    if (result.ok && result.result && result.result.ok && result.result.result && result.result.result.ok) {
                        const data = result.result.result;
                        resultDiv.className = 'result success';
                        resultDiv.textContent = JSON.stringify(data, null, 2);
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = 'Error: ' + (result.error || result.result?.error || result.result?.result?.error || 'Unknown error');
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = 'Error: ' + error.message;
                }
            }

            async function evaluateResponse() {
                const query = document.getElementById('eval-query').value;
                const response = document.getElementById('eval-response').value;
                const quality = document.getElementById('eval-quality').value;
                const resultDiv = document.getElementById('evaluate-result');

                resultDiv.textContent = 'Evaluating response...';
                resultDiv.className = 'result';

                try {
                    const fetchResponse = await fetch('/admin/response/evaluate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            query: query,
                            response: response,
                            expected_quality: quality
                        })
                    });

                    const result = await fetchResponse.json();

                    if (result.ok && result.result && result.result.ok && result.result.result && result.result.result.ok) {
                        const data = result.result.result;
                        resultDiv.className = 'result success';
                        resultDiv.textContent = JSON.stringify({
                            evaluation: data.evaluation || {},
                            overall_score: data.overall_score || 'N/A',
                            quality_rating: data.evaluation?.actual_quality || 'N/A',
                            recommendations: data.recommendations || [],
                            scores: data.scores || {}
                        }, null, 2);
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = 'Error: ' + (result.error || result.result?.error || result.result?.result?.error || 'Unknown error');
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(html_content)


@router.get("/sw.js")
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

@router.get("/health")
async def health(request: Request):
    ollama_ok = False
    try:
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=2.0)
        ollama_ok = r.status_code < 400
    except Exception:
        pass

    agent_ok = await check_agent_runner_health()

    # Check streaming health
    streaming_ok = await check_streaming_health()

    # Check cache freshness
    cache_ok = True
    cache_warnings = []
    try:
        from router.health_check_helpers import check_cache_freshness
        is_fresh, stale_files = check_cache_freshness()
        cache_ok = is_fresh
        if not is_fresh:
            cache_warnings = stale_files[:3]  # First 3 for brevity
    except Exception as e:
        cache_ok = False
        cache_warnings = [f"check_failed: {str(e)[:50]}"]

    overall_ok = ollama_ok and agent_ok and cache_ok

    return {
        "status": "healthy" if overall_ok else ("degraded" if (ollama_ok and agent_ok) else "unhealthy"),
        "ok": overall_ok,
        "services": {
            "router": {"ok": True, "version": VERSION},
            "ollama": {"ok": ollama_ok},
            "agent_runner": {"ok": agent_ok},
        },
        "streaming_health": streaming_ok,
        "cache": {
            "fresh": cache_ok,
            "warnings": cache_warnings
        }
    }

@router.post("/admin/prompt/inspect")
async def inspect_prompt(request: Request, query: str = "", query_type: str = "generic"):
    """Inspect the system prompt that would be generated for a query."""
    require_auth(request)

    try:
        # Call the agent runner's prompt inspection tool
        import httpx
        agent_url = f"{state.agent_runner_url}/admin/admin/tools/execute"

        payload = {
            "tool_name": "inspect_system_prompt",
            "arguments": {
                "query": query,
                "query_type": query_type
            }
        }

        headers = {"Authorization": f"Bearer {state.router_auth_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(agent_url, json=payload, headers=headers, timeout=30.0)

        if response.status_code == 200:
            result = response.json()
            # Return the full nested response - frontend can handle extraction
            return result
        else:
            return {"ok": False, "error": f"Agent runner returned {response.status_code}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/admin/query/analyze")
async def analyze_query(request: Request, query: str = ""):
    """Analyze how a query would be classified."""
    require_auth(request)

    try:
        # Call the agent runner's query analysis tool
        import httpx
        agent_url = f"{state.agent_runner_url}/admin/admin/tools/execute"

        payload = {
            "tool_name": "analyze_query_classification",
            "arguments": {
                "query": query
            }
        }

        headers = {"Authorization": f"Bearer {state.router_auth_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(agent_url, json=payload, headers=headers, timeout=30.0)

        if response.status_code == 200:
            result = response.json()
            # Return the full nested response - frontend can handle extraction
            return result
        else:
            return {"ok": False, "error": f"Agent runner returned {response.status_code}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/admin/response/evaluate")
async def evaluate_response(request: Request, query: str = "", response: str = "", expected_quality: str = "high"):
    """Evaluate the quality of an AI response."""
    require_auth(request)

    try:
        # Call the agent runner's response evaluation tool
        import httpx
        agent_url = f"{state.agent_runner_url}/admin/admin/tools/execute"

        payload = {
            "tool_name": "evaluate_response_quality",
            "arguments": {
                "query": query,
                "response": response,
                "expected_quality": expected_quality
            }
        }

        headers = {"Authorization": f"Bearer {state.router_auth_token}"}
        async with httpx.AsyncClient() as client:
            response_result = await client.post(agent_url, json=payload, headers=headers, timeout=30.0)

        if response_result.status_code == 200:
            result = response_result.json()
            return result
        else:
            return {"ok": False, "error": f"Agent runner returned {response_result.status_code}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/stats")
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
