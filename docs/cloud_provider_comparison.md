# Cloud Provider Strategy: Replicate vs Modal vs API

## Executive Summary
For the "Anti-Bankruptcy" $1/day strategy, **Token-Based API Providers** (DeepInfra, Fireworks, Replicate) are superior to **Time-Based GPU Renters** (Modal, RunPod) for the specific use case of sporadic batch processing.

## The Economics of $1.00

### 1. The Heavyweight: Llama-3.1-405B (GPT-4 Class)
This is the model you want for "Code Janitor" and "Memory Audit".

*   **API (Token-Based)**:
    *   **Cost:** ~$3.00 per 1M tokens (DeepInfra/Fireworks).
    *   **$1.00 buys:** **~330,000 tokens**.
    *   **Capacity:** Roughly **1,000 pages** of code/text.
    *   **Risk:** Zero. You pay for what you read.

*   **Modal (Time-Based)**:
    *   **Cost:** ~$4.00 per hour (H100).
    *   **$1.00 buys:** **15 minutes**.
    *   **Throughput:** 405B is slow. On a single H100, it might run at 10-15 tokens/sec.
    *   **Total Output:** 15 mins * 60s * 15 tok/s = **13,500 tokens**.
    *   **Comparison:** You get **24x LESS** output for your dollar because you are paying for the massive VRAM to just "sit there" while it computes slowly.

### 2. The Workhorse: Llama-3.3-70B (High-Speed)
This is for "Auto-Tagger" and general RAG.

*   **API (Token-Based)**:
    *   **Cost:** ~$0.60 per 1M tokens.
    *   **$1.00 buys:** **1.6 Million tokens**.
    *   **Capacity:** Entire libraries of content.

*   **Modal (Time-Based)**:
    *   **Cost:** ~$4.00 per hour (H100).
    *   **Throughput:** 100+ tokens/sec.
    *   **Total Output:** 15 mins * 60s * 100 tok/s = **90,000 tokens**.
    *   **Comparison:** You get **17x LESS** output.

## Verdict: The "API" Route Wins
Unless you are running a custom training job or a very specialized non-LLM Python script (e.g., heavily custom OpenCV pipelines), **renting raw GPUs is mathematically bad for batched inference.**

The API providers subsidize the cost by batching thousands of users onto that H100. You cannot compete with their efficiency using a single rented box.

### Recommended Provider "DeepInfra" or "Fireworks"
*   **Why:** They offer the **OpenAI-Compatible API** standard (drop-in replacement for your config).
*   **Pricing:** Aggressive (~$3/1M for 405B).
*   **Models:** They host the full 405B BF16 precision models.

### How to Switch
1.  Get a key from DeepInfra/Fireworks/Replicate.
2.  Put it in `providers.yaml` under `hypercompute`.
3.  Set `base_url` to `https://api.deepinfra.com/v1/openai` (or equivalent).
4.  Enjoy **300,000 tokens per night** for $1.00.
