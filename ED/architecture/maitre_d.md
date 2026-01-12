# Maître d' (Intent & Tool Selection)

**Maître d'** (The Head Waiter) is the system's intent classification and context optimization engine. It dynamically curates the "Menu" of tools available to the agent for each turn.

**Source**: `ai/agent_runner/intent.py`

---

## 1. Constraint Logic Table

The heart of the Maître d' is a set of rigorous constraints injected into the classification prompt.

| ID | Trigger Scope | Action / Selection | Logic Description |
| :--- | :--- | :--- | :--- |
| **1** | **Core Tools** | **SKIP** | Time/Location are pre-loaded; never select them (redundancy). |
| **3** | **General Web** | Select `fetch`, `browse` | Generic web access requests. |
| **4** | **Filesystem** | Select `filesystem` | "read", "write", "list", "file" operations. |
| **5** | **Sys Admin** | Select `system`, `admin` | Command execution, health checks. |
| **5.5** | **Introspection** | Select `system`, `admin` | "How does it work?", "Show config", "Model architecture". |
| **6** | **Advice** | Select `advice_topics` | Dynamic mapping to available advice modules. |
| **7** | **Local Action** | Set `system_action` | "help", "prompt", "restart", "emoji". |
| **8** | **Layer Control** | Set `system_action` | "enable/disable layer". |
| **9** | **News/Headlines** | Select `tavily-search` | "today's news", "headlines", "Google news". |
| **10** | **Real-Time** | Select `tavily-search` | "breaking", "current events", "time-sensitive". |
| **11** | **Memory** | Select `memory` | "recall", "remember", "preferences". |

---

## 2. JSON Schema Output

Maître d' performs "Chain of Thought" internally but outputs strictly formatted JSON.

| Field | Type | Description |
| :--- | :--- | :--- |
| `target_servers` | `List[str]` | List of MCP server names to load (e.g., `["filesystem", "tavily-search"]`). |
| `advice_topics` | `List[str]` | List of advice keys to inject into context. |
| `system_action` | `str \| null` | Specialized action for Nexus (e.g., `prompt`, `restart`). |

---

## 3. The Learning Loop (Hybrid Scoring)

Maître d' integrates with `ai/agent_runner/feedback.py` to learn from past success.

**Input**: User Query + Historical Logs (`maitre_d_feedback.json`)
**Algorithm**:
$$ Score = (Overlap + Coverage + (0.4 \times Fuzzy)) \times RecencyWeight $$

**Injection**:
If `Score > Threshold`, the server is appended to the prompt:
> *"Recall: User usage history suggests these servers are relevant: [ServerA, ServerB]"*

---

## 4. Query Refinement

Before classification, ambiguous queries are rewritten.

| User Input | Generated Query | Model Used |
| :--- | :--- | :--- |
| "Find it." | "Find the budget.py file mentioned in the previous error." | `QUERY_REFINEMENT_MODEL` |
| "Turn it up." | "Increase volume on Sonos speaker." | `QUERY_REFINEMENT_MODEL` |

**Context**: Uses last 3 messages only (for speed).
