# Cloud vs. Local GPU Strategy: "The Anti-Bankruptcy Plan"

## 1. The Core Trade-off

You have "time overnight" (local is free) vs. "robust enhancement" (cloud is powerful but costly).

| Feature | Local Mac (M-Series) | Rented GPU (Vast/RunPod) | Serverless GPU (Modal/Replicate) |
| :--- | :--- | :--- | :--- |
| **Cost** | **$0.00** (Sunk Cost) | $0.20 - $0.60 / hr | Pay per second (~$1.80/hr) |
| **Idle Risk** | None | **High** (Forgot to turn off = $$$) | **Zero** (Auto-scales to 0) |
| **Privacy** | High (Local storage) | Low (Public marketplace) | Medium (Ephemeral containers) |
| **Setup** | Ready | High Maintenance (SSH, drivers) | Medium (Python SDK) |
| **Use Case** | Text, small RAG, OCR | Training, Long-running Jobs | **Burst Inference, Heavy Vision** |

## 2. Recommendation: The "Hybrid Night Shift"

Do not rent a standing GPU instance. It is too easy to burn money if a script hangs or you forget to un-rent it.

Instead, use a **Serverless** approach for "heavy lifting" only, and use your Mac for the "churn".

### Phase A: Local Night Operations (Free)
Your Mac is powerful enough to run `llama3.3` or `mistral` all night.
*   **Tasks**: Summarize daily logs, Extract Entities (Graph), Re-rank RAG results.
*   **Cost**: $0.
*   **Action**: We tune your `rag_ingestor.py` and `memory_tasks.py` to run full-throttle between 1 AM and 6 AM.

### Phase B: Cloud "Sniper" Shots (Paid, Capped)
Use cloud *endpoints* (not instances) for tasks your Mac fails at or is too slow for.
*   **Tasks**: 
    *   **Vision**: Describing complex diagrams/PDFs (Local vision models are still weak compared to GPT-4o/Claude-3.5).
    *   **Deep Reasoning**: "What implies X?" over 1000 documents (Needs 405B model or massive context window).
*   **Control**: Hard hard-cap using API spend limits ($5/month).

## 3. Implementation Plan

1.  **Refactor `rag_ingestor.py`**:
    *   Replace hard-coded OpenAI calls with a `GLM` (Generic Language Model) wrapper.
    *   Allow switching between `ollama:local` (Night) and `openai/replicate` (Burst).
2.  **Create `night_scheduler.py`**:
    *   Wakes up at 1 AM.
    *   Checks `agent_fs_root/ingest` queue size.
    *   Runs local models to process text.
    *    *Only* routes images/audio to cloud if they stall the local queue.
3.  **Bankruptcy Protection**:
    *   Use **Router Circuit Breakers**: Configuring the Router to reject Cloud requests if a daily budget variable is exceeded.

## 4. Why this is better than Renting
*   **Renting**: You pay for the time to `apt-get install`, transfer files, debug errors, and idle time.
*   **Serverless/API**: You pay only for the *inference*. If you process 50 files, you pay for exactly 50 files.

**Verdict**: We stick to **Local First**, and add **Serverless Fallback** for specific "Enhancement" tasks that require model sizes > 32GB VRAM.
