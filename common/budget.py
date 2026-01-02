
import json
import logging
import time
import os

# Simple file-based budget tracker because we don't want a full database
BUDGET_FILE = os.path.expanduser("~/ai/budget.json")
logger = logging.getLogger("common.budget")

class BudgetTracker:
    def __init__(self, daily_limit_usd: float = 10.00):
        self.daily_limit_usd = daily_limit_usd
        self.current_spend = 0.0
        self.last_reset = time.time()
        self.alert_level = 0 # 0=None, 1=80%, 2=90%, 3=100%
        self._load()

    def _load(self):
        try:
            if os.path.exists(BUDGET_FILE):
                with open(BUDGET_FILE, "r") as f:
                    data = json.load(f)
                    self.current_spend = data.get("current_spend", 0.0)
                    self.last_reset = data.get("last_reset", time.time())
                    self.daily_limit_usd = data.get("daily_limit_usd", self.daily_limit_usd)
                    
            # Check if we need to reset (Daily 00:00 UTC, or just 24h cycle? 24h is simpler)
            if time.time() - self.last_reset > 86400:
                self.reset()
        except Exception as e:
            logger.error(f"Failed to load budget: {e}")

    def _save(self):
        try:
            with open(BUDGET_FILE, "w") as f:
                json.dump({
                    "current_spend": self.current_spend,
                    "last_reset": self.last_reset,
                    "daily_limit_usd": self.daily_limit_usd
                }, f)
        except Exception as e:
            logger.error(f"Failed to save budget: {e}")

    def reset(self):
        logger.info(f"Budget reset. Previous spend: ${self.current_spend:.4f}")
        self.current_spend = 0.0
        self.last_reset = time.time()
        self.alert_level = 0
        self._save()

    def record_usage(self, provider: str, cost_usd: float):
        """Record a successful API call cost and trigger alerts."""
        self.current_spend += cost_usd
        self._save()
        
        ratio = self.current_spend / self.daily_limit_usd
        
        # Alert Logic
        from common.notifications import notify_high, notify_critical
        
        if ratio >= 1.0 and self.alert_level < 3:
            notify_critical(
                title="Daily Budget Exceeded",
                message=f"Spending (${self.current_spend:.2f}) has hit the limit (${self.daily_limit_usd:.2f}). Cloud models are now BLOCKED.",
                source="BudgetTracker"
            )
            self.alert_level = 3
        elif ratio >= 0.9 and self.alert_level < 2:
             notify_high(
                title="Budget Warning (90%)",
                message=f"Spending is at 90% (${self.current_spend:.2f} / ${self.daily_limit_usd:.2f}).",
                source="BudgetTracker"
            )
             self.alert_level = 2
        elif ratio >= 0.8 and self.alert_level < 1:
             notify_high(
                title="Budget Warning (80%)",
                message=f"Spending is at 80% (${self.current_spend:.2f} / ${self.daily_limit_usd:.2f}).",
                source="BudgetTracker"
            )
             self.alert_level = 1

    def check_budget(self, estimated_cost: float = 0.0) -> bool:
        """Returns True if request is allowed, False if budget exceeded."""
        if self.current_spend + estimated_cost > self.daily_limit_usd:
            logger.error(f"⛔ Budget Blocked: Request would exceed limit (${self.current_spend:.4f} >= ${self.daily_limit_usd:.2f})")
            
            # Ensure critical alert is sent if we are blocked (idempotent via alert_level)
            if self.alert_level < 3:
                from common.notifications import notify_critical
                notify_critical(
                    title="Daily Budget Exceeded",
                    message=f"Spending (${self.current_spend:.2f}) has hit the limit (${self.daily_limit_usd:.2f}). Request blocked.",
                    source="BudgetTracker"
                )
                self.alert_level = 3
                
            return False
        return True

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Rough estimation of cost."""
        # Pricing Table (Apr 2024 / Dec 2025 Estimates)
        # H100 Serverless: ~$0.003 - $0.005 per 1k tokens? No, usually per second.
        # But we track tokens as proxy.
        
        rate_in = 0.0
        rate_out = 0.0
        
        if "gpt-4o" in model and "mini" not in model:
            rate_in = 5.00 / 1_000_000
            rate_out = 20.00 / 1_000_000
        elif "gpt-3.5" in model or "gpt-4o-mini" in model:
            rate_in = 0.60 / 1_000_000
            rate_out = 2.40 / 1_000_000
        elif "claude-3-opus" in model:
            rate_in = 15.00 / 1_000_000
            rate_out = 75.00 / 1_000_000
        elif "claude-3.5-sonnet" in model:
            rate_in = 3.00 / 1_000_000
            rate_out = 15.00 / 1_000_000
        elif "llama-3" in model and ("replicate" in model or "deepinfra" in model):
             # Llama 3 405B is roughly $3-5 / 1M tokens
             rate_in = 3.00 / 1_000_000
             rate_out = 3.00 / 1_000_000
        elif "grok" in model:
            # Grok-2 (Dec 2024 pricing): ~$5 / $10 roughly similar to GPT-4o-mini/Standard mix
            # Actually Grok-2-1212 is efficient. Let's assume standard high-tier.
            rate_in = 2.00 / 1_000_000
            rate_out = 10.00 / 1_000_000
             
        return (input_tokens * rate_in) + (output_tokens * rate_out)

# Singleton
_tracker = None
def get_budget_tracker() -> BudgetTracker:
    global _tracker
    if _tracker is None:
        _tracker = BudgetTracker()
    return _tracker
