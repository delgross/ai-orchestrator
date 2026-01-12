# Budgeting & Cost Control

**Antigravity** includes a sovereign financial safety system that enforces strict budget limits on AI model usage. This system operates locally, independent of cloud provider limits, to prevent "bill shock."

**Source**: `ai/common/budget.py`

---

## 1. Budget Tracker

The `BudgetTracker` is a singleton service that maintains a daily spending ledger. It is designed to be **fail-closed**: if the budget is exceeded, all paid model requests are blocked immediately.

### Core Logic

- **Storage**: `~/ai/budget.json` (Simple persistent state).
- **Reset Cycle**: Resets automatically every 24 hours.
- **Default Limit**: $10.00 USD / day (adjustable).

### Blocking Mechanism

Before any request is sent to a paid provider (OpenAI, Anthropic, etc.), the `check_budget()` method is called:

```python
if tracker.current_spend >= tracker.daily_limit_usd:
    # BLOCKS request
    logger.error("⛔ Budget Blocked")
    return False
```

---

## 2. Alert Escalation

The system uses a 3-stage escalation protocol based on the `usage / limit` ratio:

| Level | Threshold | Action |
| :--- | :--- | :--- |
| **0** | < 80% | Normal Operation. |
| **1** | **80%** | `notify_high`: "Budget Warning (80%)". |
| **2** | **90%** | `notify_high`: "Budget Warning (90%)". |
| **3** | **100%** | `notify_critical`: "Daily Budget Exceeded. Cloud models BLOCKED." |

**Idempotency**: The `alert_level` state ensures users are not spammed with notifications for every request once a threshold is crossed.

---

## 3. Cost Estimation

The `estimate_cost` function provides local estimation of token costs. While not the official billing record, it is accurate enough for safety enforcement.

**Supported Pricing (Estimated)**:
- **GPT-4o**: ~$5/M in, $20/M out.
- **Claude 3.5 Sonnet**: ~$3/M in, $15/M out.
- **Small Models (3.5/Mini)**: ~$0.60/M in.
- **Local Models (Ollama)**: $0.00 (Always allowed).

**Note**: The system prioritizes local models (Ollama) which bypass the budget check entirely, ensuring the agent remains functional (albeit less capable) even when the budget is exhausted.
