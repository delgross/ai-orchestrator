# Learning Loop (Maître d' Feedback)

The **Learning Loop** allows the system to improve its tool selection over time. It "remembers" which tools successfully resolved specific user queries and prioritizes them in future similar contexts.

**Source**: `ai/agent_runner/feedback.py`

---

## 1. Concept: Feedback Storage

The system maintains a persistent knowledge base of successful query-tool pairs in `ai/agent_data/maitre_d_feedback.json`. This acts as a "long-term memory" for tool utility.

### Data Structure
```json
{
    "query": "read the project documentation",
    "server": "fs_reader",
    "timestamp": 1715000000.0,
    "query_hash": "a1b2c3d4"
}
```

- **Query Hash**: Used for O(1) deduplication.
- **Timestamp**: Used for recency weighting (knowledge decay).
- **Server**: The target MCP server that was successfully used.

---

## 2. Recording Success

When a user expressly praises a result or a workflow completes successfully, `record_tool_success()` is called.

**Constraints**:
- **Core Exclusion**: Core servers (`project-memory`, `system-control`) are never recorded (they are omnipresent).
- **Deduplication**: Prevents storing identical query-server pairs.
- **Size Limit**: Trims old records when > 10,000 entries (FIFO with 20% retention buffer).
- **Concurrency**: Uses `fcntl.flock` (File Locking) to ensure multi-process safety (e.g., multiple agents writing simultaneously).

---

## 3. Suggestion/Retrieval Algorithm

The `get_suggested_servers` function ranks tools for a new query using a **Hybrid Scoring System**:

$$ Score = (Overlap + Coverage + (0.4 \times Fuzzy)) \times RecencyWeight $$

1.  **Keyword Overlap**: Exact matches of meaningful words.
2.  **Fuzzy Similarity**: `difflib.SequenceMatcher` ratio for handling typos/variations.
3.  **Recency Weight**: Exponential decay with a 3-day half-life. Recent successes are weighted higher than old ones.

**Result**: A list of server names that are injected into the Maître d's "Advice Menu," influencing the `intent.py` selection logic to pick these proven tools.
