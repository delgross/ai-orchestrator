# Chat Interface Command Reference

This document details specific **actions** and **commands** available in the Chat Interface that go beyond normal conversation. The Agent is trained to recognize these intents and map them to system tools.

## 🛠 System Status & Health
*   **"Check system health"** / **"Show circuit breakers"** / **"System status"**
    *   **Action**: Runs a diagnostic check across the Router and Agent.
    *   **Output**: Returns a live Markdown table showing:
        *   Overall System Status (Healthy/Degraded)
        *   Critical Issue Count
        *   **Circuit Breaker States** (closed=🟢, open=🔴) for all services (Ollama, Agent, RAG).

## ⚡️ Task Management
*   **"Trigger [Task Name]"**
    *   *(e.g., "Trigger night shift", "Run memory backup", "Run daily research")*
    *   **Action**: Manually forces a registered background task to execute immediately, bypassing its schedule.
*   **"Consolidate memory"**
    *   **Action**: Forces the Memory Consolidation cycle. This reads recent chat episodes and extracts "Facts" into SurrealDB. Useful if you want to ensure the agent "remembers" the current session immediately.

## 🧠 Knowledge Management
*   **"Ingest this: [text]"** / **"Add to knowledge base: [text]"**
    *   **Action**: Saves the provided text into the **RAG (Vector Database)**.
    *   **Use Case**: Storing permanent business rules, reference data, or difficult context that shouldn't be lost.
*   **"Search for [topic]"**
    *   **Action**: Explicitly triggers the `unified_search` tool.
    *   **Scope**: Searches both Short-term Semantic Memory (Facts) and Long-term RAG Documents (PDFs, Manuals).

## 🚨 Developer Feedback
*   **"I need a tool to [do X]"** / **"Report missing tool: [Name]"**
    *   **Action**: Logs a structured "Missing Tool Request" to `missing_tools.md`.
    *   **Use Case**: When you encounter a limitation (e.g., "I need a tool to resize images"), report it here to prioritize its development.

## 🔌 Connected Tools (MCP)
The Available Tools menu (Maître d') allows the agent to dynamically select tools from connected servers:

| Domain | Example Query |
|---|---|
| **Filesystem** | "List files in `ai/config`", "Read `main.py`" |
| **System** | "Restart the agent runner" (Requires Admin context) |
| **Time/Weather**| "Time in Tokyo", "Weather in Ohio" |
| **Cloud** | "Check H100 Uplink status" (via Cloud MCP) |

---
*Note: This documentation should be updated as new tools are registered in `executor.py`.*
