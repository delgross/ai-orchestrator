# System Capabilities & State

**Antigravity** defines its capabilities not just by the code it runs, but by the dynamic state it maintains. This includes Model Roles, Operational Modes, and Tempo.

**Source**: `ai/agent_runner/state.py`

---

## 1. Agent State & Flags

The `AgentState` class is the runtime sovereign of the system. It holds the "Self" of the agent.

### Core Flags
| Flag | Env Var | Description |
| :--- | :--- | :--- |
| `router_enabled` | `ROUTER_ENABLED` | If false, bypasses complex routing logic. |
| `finalizer_enabled` | `FINALIZER_ENABLED` | Controls the post-processing refinement step. |
| `fallback_enabled` | `FALLBACK_ENABLED` | Allows degrading to lower-tier models on failure. |
| `degraded_mode` | (Runtime) | **True** if critical dependencies (like DB) are missing. |

### Model Roles (The "Self")
The system is composed of multiple specialized intelligences, defined in `AgentState`:

- **Agent Model**: General purpose executor.
- **Intent Model**: Classifier for user requests.
- **Planner/Pruner**: Context optimization.
- **Healer**: Specialized stable model for fixing broken JSON/Code (`qwq`).
- **Critic**: Analysis model (`qwen3`).
- **Vision**: Multimodal capabilities (`llama3.2-vision`).

---

## 2. Operational Modes

The agent operates in distinct "Modes" that configure its personality and tool access. Modes are loaded from config but tracked in `state._active_mode`.

- **Chat**: Standard conversational interface.
- **Coding**: Specialized for file manipulation and syntax correctness.
- **Architect**: High-level planning, no code execution.
- **Writer**: Prose generation, reduced technical constraints.

---

## 3. Tempo System

The system tracks user presence and idleness to adjust its "Tempo" (`state.Tempo`).

| Tempo | Trigger | Behavior |
| :--- | :--- | :--- |
| **FOCUSED** | < 60s idle | High polling, immediate responses. User is present. |
| **ALERT** | < 5m idle | Standard polling. User likely present. |
| **REFLECTIVE** | < 30m idle | "Active Research" phase. background tasks allowed. |
| **DEEP** | > 30m idle | Maintenance mode. Garbage collection, indexing. |

---

## 4. Quality Tiers

The system supports dynamic Quality Tiers to balance cost vs. intelligence.

**Source**: `ai/agent_runner/quality_tiers.py`

- **Tier Configuration**:
    - `skip_refinement`: Tradeoff speed for polish.
    - `memory_retrieval_limit`: Tradeoff context size for cost.
    - `architecture_context_limit`: Depth of system knowledge injected.
- **Tiers**:
    - `SPEED`: Minimal context, fastest models (Haiku/Flash).
    - `BALANCED`: Default. Good mix.
    - `HIGH_QUALITY`: Full context, reasoning models (Opus/O1).

## 5. Circuit Breakers

**Registry**: `state.mcp_circuit_breaker`

The system protects itself from failing subsystems using the **Circuit Breaker** pattern. If an MCP server fails repeatedly (default: 5 times in 60s), the breaker "opens," and the server is temporarily removed from the tool menu to prevent cascading latency.
