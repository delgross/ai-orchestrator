# System Audit: Recent Changes & System State

**Time Range:** Last ~12 Hours (Approx.)
**Focus:** Modifications, Bypasses, Disabled Features, and "Destroyed" Code.

## 1. "Destroyed" (Reverted/Removed)
The following code was actively removed to restore system stability:

- **Healer Verification Protocol**:
    - **Status:** [DESTROYED / REVERTED]
    - **Details:** All code related to the "Healer Escalation" verification was reverted. This includes:
        - `tests/force_healer.py` (Likely deleted)
        - Modifications to `agent_runner/engine.py` (Trigger logic removed)
        - `bin/run_agent_runner.sh` (Restored to original state)
    - **Reason:** To restore the codebase to a clean pre-verification state.

- **JIT Internet Check (Engine)**:
    - **Status:** [REMOVED]
    - **Location:** `agent_runner/engine.py` (Line ~355)
    - **Details:** The "Just-In-Time" internet connectivity check before prompt generation was removed.
    - **Reason:** To prevent blocking prompt generation on network latency ("flapping" state). The system now relies on a background health monitor.

## 2. Model & Maître d' Architecture (Deep Dive)

### Maître d' (Local Routing Logic)
- **Mechanism:** The `AgentEngine` in `engine.py` (lines 34-53) now implements a "Fast Lane" routing logic.
- **Change:**
    - **Local Models (`ollama:*`, `local:*`)**: Bypass the main Router (Port 5455) and connect **directly** to Ollama (Port 11434).
        - *Reason:* Optimization to fix streaming latency and buffering issues.
    - **Remote Models**: Continuing to use the governed Router path (Port 5455).

### The "Rogue Six" (Model Roster)
Configuration source: `sovereign.yaml` (The Single Source of Truth).
- **Agent:** `ollama:mistral:latest` (Speed + Intelligence)
- **Router (Maître d'):** `ollama:mistral:latest` (Optimized for speed)
- **Healer:** `ollama:qwen3:30b` (Balanced for diagnostics)
- **Auditor:** `ollama:qwen3:30b` (Balanced for fact-checking)
- **Summarizer:** `ollama:mistral:latest` (Speed)
- **Vision:** `Qwen/Qwen2.5-VL-72B-Instruct-AWQ` (Cloud-based via Modal)

### Maître d' Telemetry
- **Feature:** Log Selection Precision (Feature 9)
- **Status:** Active in `engine.py` (line 589).
- **Function:** Tracks how many tools were *actually used* vs *provided* to optimize context window usage.

## 3. Bypassed & Disabled Components
The following features are currently disabled or operating in a bypassed state:

- **MCP Servers**:
    - **Weather Service**: [DISABLED] (`circuit_breaker_opened`)
    - **Brave Search**: [DISABLED] (`circuit_breaker_opened`)
    - **Status:** These servers triggered failure thresholds and were auto-disabled by the circuit breaker.

- **Router Authentication**:
    - **Status:** [BROKEN / BLOCKING]
    - **Issue:** The `ROUTER_AUTH_TOKEN` is enabled (`antigravity_router_token_2025`) but is **not being passed** by internal system components (specifically `project-memory`).
    - **Effect:** Internal calls are failing with `401 Unauthorized`, causing the "Hydration" hang.
    - **Pending Fix:** We are about to patch this by propagating the token properly.

- **Budget System Security**:
    - **Status:** [FAIL OPEN]
    - **Location:** `agent_runner/engine.py` (Line 81)
    - **Details:** `fail_open_on_budget_error` is set to `True`.
    - **Effect:** If the budget tracker fails, the system allows requests to proceed rather than blocking them. This "bypasses" strict budget enforcement for reliability.

- **Model Routing (Local Models)**:
    - **Status:** [BYPASSED]
    - **Location:** `agent_runner/engine.py` (Line 42)
    - **Details:** Models starting with `ollama:` or `local:` **bypass the Router** completely and talk directly to the Ollama port (11434).
    - **Reason:** To fix streaming chunk buffering and reduce latency for local models.

## 3. Notable Modifications (Recent Work)
- **Context Hydration (Performance Logging)**:
    - **Status:** [MODIFIED]
    - **Details:** Logging was added to `agent_runner/engine.py` to track "Architecture Hydration" time. This telemetry revealed the 30s timeout/hang caused by the Auth Deadlock.
- **Model Optimization**:
    - **Status:** [CHANGED] (Previous Session)
    - **Details:** `mcp_model` was switched from `ollama:llama3.3` (slow) to `openai:gpt-5.1` (fast) to fix tool latency.

## Summary recommendation
The system is currently stable but suffering from a **Self-Denial of Service** due to the Auth Deadlock in the Context Hydration feature. The "Healer" code is clean. Several MCP servers need manual reset or debugging (`weather`, `brave-search`).

**Immediate Action:** Execute the pending fix for `ROUTER_AUTH_TOKEN` propagation to resolve the Hydration crash.
