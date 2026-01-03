---
kb_id: default
authority: 0.5
ingested_at: 2026-01-02 14:49:53
keywords: [source_folder:5e01b889-041c-46a1-9732-7a3c5e393120]
---
# Transcription of system_lexicon
**Summary:** 
---
# Antigravity System Lexicon

## 1. Core Services & Topography
| Service Name | Alias | Port | New Terminology | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Router** | `local.ai.router` | **5455** | **Gateway** | Entry point. Handles auth, rate limiting, and routing. |
| **Agent Runner** | `local.ai.agent_runner` | **5460** | **Cortex** | The brain. Executes tasks, manages context, and "thinks". |
| **RAG Server** | `local.ai.rag_server` | **5555** | **Memory** | Handles vector ingestion, storage, and retrieval. |
| **SurrealDB** | `local.ai.surrealdb` | **8000** | **Database** | The archive. Stores all structured data. |

## 2. Functional Components ( "The Slang" )

### Orchestrator
*   **Definition**: The Program (Me).
*   **Role**: The overarching system and intelligence that manages all other components.

### Observer
*   **Definition**: The system-wide health monitor (`agent_runner/health_monitor.py`).
*   **Role**: Oversees the entire system, monitors connectivity, and triggers self-healing.
*   **Mechanism**: Periodic health checks + Circuit Breakers.

### Diagnostician
*   **Definition**: The intelligent system that analyzes error patterns.
*   **Input**: **Sorter** (Real-time log stream).
*   **Role**: Detects cascades (e.g., "Flood detected") and auto-heals.
*   **Output**: `logs/live_stream.md`.

### Blob
*   **Definition**: A massive contiguous text payload (>500KB) with no natural break points.
*   **Handling**: Processed in background to prevent blocks.

### Maître d'
*   **Definition**: The intent classification system (`intent.py`).
*   **Role**: Analyzes your request and hands you the correct "Menu" of tools (e.g., flight tools vs. coding tools) to prevent hallucination.

## 3. Data Structure Terms

### Episode
*   **Definition**: A single cycle of "Think -> Act -> Observe".
*   **Usage**: "The agent completed 5 episodes to solve the task."

### Memory Banks
*   **Definition**: Distinct Knowledge Bases (e.g., "Default", "Shadow", "Codebase") stored within **Memory**.

### Memory Tiers
*   **Context Window**: The **Workbench**. The immediate limit (e.g. 128k) where the Active Brain loads data to think.
*   **Short Term Memory**: The **Buffer**. Ingested data sits here for ~2 days to be queried quickly. High resolution.
*   **Long Term Memory**: The **Archive**. Data older than 2 days is consolidated, summarized, and moved here by the "Memory Consolidation" task.
*   **Permanent Memory**: The **Knowledge Base** (Artifacts & Code). Immutable "Truths" (e.g., this Lexicon) that persist until manually rewritten.

### MCP Server
*   **Definition**: Model Context Protocol Server.
*   **Role**: External tool providers (e.g., "Flight Search", "Google Drive") that the Cortex connects to.

## 4. Perspectives & Roles

### DevOps View
*   **Conductor**: `manage.sh`. The script that starts/stops the orchestra.
*   **Governor**: `circuit_breaker.py`. Stops runaway processes or crashing services.
*   **Accountant**: `budget.py`. Tracks token usage and costs.

### Developer View
*   **Gauntlet**: `tests/torture_*.py`. The stress testing suite.
*   **Registry**: `agent_runner/registry.py`. The central lookup for tools and services.
*   **Modal**: The bridge to Cloud H100 GPUs (running Qwen2-VL, etc.).

### User View
*   **God Mode**: The persona enabling unrestricted system access.
*   **Live Stream**: The `logs/live_stream.md` file acting as the system pulse.
*   **Cloud Brain**: The cluster of H100s used for heavy lifting (Image Analysis, Nightly Optimization).

## 5. Autonomous Agents
*   **Janitor**: `maintenance_tasks.py`. Weekly code reviewer and cleaner.
*   **Sentry**: Visual anomaly detector. Compares new images against "Golden References".
*   **Auto-Tagger**: Generates metadata for ingested assets (images/files).
*   **Graph Optimizer**: Nightly process that clusters knowledge and improves retrieval.

## 6. Intelligence Layers
*   **Active Brain**: `Grok 3 (xai:grok-3)`. The default persona you chat with.
*   **Architect Brain**: `Llama 3.3 70B`. Uses high-context for project structure and design. I am usually this.
*   **Mechanic Brain**: `Llama 3.1 8B`. Fast, local model for log analysis and health checks.
*   **Automator Brain**: `GPT-4o Mini`. Cheap, fast model for browser and OS interactive tasks.
*   **Researcher Brain**: `GPT-4o / o1`. High-reasoning model for complex queries and web synthesis.
*   **Vision**: `Qwen2.5-VL-72B`. The eyes of the system (running on Modal H100s).
*   **Embedder**: `mxbai-embed-large`. The Translator. Converts text into math coordinates for the Memory Database.
*   **Modal Auditor**: `RoBERTa-MNLI`. The Judge. Detects lies and contradictions between facts during the Night Shift.
