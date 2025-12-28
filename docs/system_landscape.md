# System Landscape & Role Definitions

This document outlines the architecture of the AI Orchestrator, defining the specific responsibilities of each LLM role and how they interact to provide a robust, resilient agentic system.

## 1. Core Agent Roles

These models drive the primary "Thinking" loop of the application.

### **Agent Runner (The Worker)**
*   **System ID:** `agent_model`
*   **Primary Function:** Execution & Tool Use.
*   **Description:** This model runs the main execution loop. It receives the user's initial prompt, decides which tools to call (filesystem, search, memory), and aggregates the results. It is optimized for speed and function-calling reliability rather than deep philosophical reasoning.
*   **Typical Model:** `gpt-4o-mini` or `claude-3-haiku`.

### **Finalizer (The Boss)**
*   **System ID:** `finalizer_model`
*   **Primary Function:** Synthesis, Reasoning, & Quality Assurance.
*   **Description:** Once the Agent Runner has finished gathering data and executing tasks, the "Episode" history is handed over to this model. The Finalizer reviews the user's request against the tools' outputs and generates the definitive, high-quality response. It acts as the "Brain" ensuring the output is coherent and intelligent.
*   **Typical Model:** `gpt-5`, `gpt-4o`, or `claude-3.5-sonnet`.

### **Fallback Engine (The Safety Net)**
*   **System ID:** `fallback_model`
*   **Primary Function:** Redundancy & Reliability.
*   **Description:** If the Finalizer (typically a cloud model) fails due to internet outages or API errors, the system automatically attempts to generate the final response using this model. It ensures the user always receives an answer.
*   **Typical Model:** A robust local model like `llama3.3:70b`.

---

## 6. Offline Autonomy ("Gravity Mode")
The system automatically ensures continuous operation during network failures or offline usage.

**Mechanism:**
- **Heartbeat:** Checks `google.com` every **15 seconds** to verify connectivity.
- **State Awareness:** Updates global `state.internet_available` flag.

**Behavior when Offline:**
1.  **Universal Model Interception:** Any request targeting a remote provider (`openai:*`, `anthropic:*`, `gpt-*`) is **intercepted** by the Agent Engine.
2.  **Automatic Substitution:** The query is re-routed instantly to the configured **Fallback Engine** (Default: `ollama:llama3.3:70b-instruct`).
3.  **Tool Protection:** Remote tools (Exa, Tavily, Firecrawl) are automatically disabled. The agent is prompted to rely on `project-memory` and `filesystem`.
4.  **Dashboard Indicators:** The "Internet" status turns **OFFLINE** (Red), giving visual confirmation of the mode switch.

**User Action Required:** None. The system adapts automatically.

## 2. Utility & Support Roles

These roles perform specialized background tasks to support the main agent.

### **Generic Tool Host**
*   **System ID:** `mcp_model`
*   **Primary Function:** Low-level Tool Execution.
*   **Description:** Some complex MCP tools require an LLM to parse unstructured data or format inputs before execution. This role handles those micro-tasks, keeping the main Agent Runner's context window clean.
*   **Typical Model:** `gpt-4o-mini` or `mistral:small`.

### **Memory & Summarization**
*   **System ID:** `summarization_model`
*   **Primary Function:** Context Compression & Fact Extraction.
*   **Description:** Runs in the background (or post-episode) to summarize long conversation threads and extract key "Facts" (Entities, Relations) for storage in the Long-Term Memory (SurrealDB).
*   **Typical Model:** `mistral:latest` or `gemma2:9b`.

### **Task Executor**
*   **System ID:** `task_model`
*   **Primary Function:** Isolated Unit Tasks.
*   **Description:** Used for single-shot operations that do not require the full conversation history, such as "Write a Python script to sort this list" or "Translate this JSON".
*   **Typical Model:** `mistral:latest` or `codellama`.

---

## 3. Infrastructure Roles

These models power the plumbing of the system.

### **Router / Gateway**
*   **System ID:** `router_model`
*   **Primary Function:** Traffic Analysis & Routing.
*   **Description:** Used internally by the Router service (`:5455`) to analyze ambiguous requests and decide which provider or agent should handle them.
*   **Typical Model:** `qwen:14b` or `mistral`.

### **Embedding Engine**
*   **System ID:** `embedding_model`
*   **Primary Function:** Vectorization (Text-to-Numbers).
*   **Description:** Converts text into vector embeddings for Semantic Search (RAG) and Long-Term Memory retrieval. Used by the Router's `/v1/embeddings` endpoint.
*   **Typical Model:** `mxbai-embed-large` or `nomic-embed-text` (Local), or `text-embedding-3` (Cloud).

---

## Architecture Diagram

```mermaid
graph TD
    User[User / LibreChat] -->|Prompt| Router(Router :5455)
    
    subgraph "Orchestrator Core"
        Router -->|Agent Request| Agent[Agent Runner :5460]
        Agent -->|Tool Calls| Tools[MCP Tools]
        Tools -->|Results| Agent
        
        Agent -->|Handover| Finalizer{Finalizer Enabled?}
        Finalizer -->|Yes| Boss[Finalizer Model (Cloud)]
        Finalizer -->|No| Answer[Return Worker Draft]
        
        Boss -.->|Error| Fallback[Fallback Engine (Local)]
    end
    
    subgraph "Memory System"
        Router -->|Embeddings| Embed[Embedding Model]
        Agent <-->|Read/Write| Memory[SurrealDB]
        Background[Summarizer] -->|Extract Facts| Memory
    end
```
