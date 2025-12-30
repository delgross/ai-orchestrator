# AI Orchestrator: Antigravity

Antigravity is a high-performance, agentic AI Orchestrator designed for resilient, offline-first personal automation. It manages a complex ecosystem of Model Context Protocol (MCP) servers, local LLMs (Ollama), and cloud providers to provide a unified "Thinking" interface.

## 🚀 Vision: "Truly Autonomous Computing"

The system focuses on:
- **Resilience**: "Gravity Mode" ensures the system never fails, switching to local models instantly during outages.
- **Efficiency**: The **Maître d'** system dynamically loads only the tools you need.
- **Observability**: A **Unified Tracking Layer** records every thought, tool call, and system transition.

## 📁 Repository Navigation

| Document | Description |
| :--- | :--- |
| [System Landscape](file:///Users/bee/Sync/Antigravity/ai/docs/system_landscape.md) | High-level logical roles (Runner, Finalizer, Fallback). |
| **[Codebase Topology](file:///Users/bee/Sync/Antigravity/ai/docs/architecture/CODEBASE_TOPOLOGY.md)** | Technical map of directories and request pathways. |
| [Maître d' System](file:///Users/bee/Sync/Antigravity/ai/docs/architecture/MAITRE_D_SYSTEM.md) | Knowledge of how tool selection and learning works. |
| [Unified Tracking](file:///Users/bee/Sync/Antigravity/ai/docs/architecture/UNIFIED_TRACKING.md) | How the system logs, blogs, and alerts. |
| [Roadmap](file:///Users/bee/Sync/Antigravity/ai/docs/architecture/roadmap.md) | The path toward full autonomous self-orchestration. |

## 🛠 Project Structure

- `agent_runner/`: The "Engine Room" - manages agent loops, memory, and tools.
- `router/`: The "Switchboard" - OpenAI-compatible proxy and provider management.
- `common/`: Shared utilities (Tracking, Anomaly Detection).
- `dashboard/`: Real-time observability and control interface.
- `config/`: System and user configuration.

## 🚦 Quick Start

1. **Configure Environment**: Copy `.env.example` to `.env` and add your keys.
2. **Start Services**: Run `./manage.sh start`.
3. **Open Dashboard**: Visit `http://localhost:3000`.

---
*For detailed implementation history, see the [Walkthrough](file:///Users/bee/.gemini/antigravity/brain/ed9b58ca-970d-4497-9aaa-49c3823ee3ed/walkthrough.md)*
