
import json
import logging
import time
import os

# Simple file-based budget tracker because we don't want a full database
BUDGET_FILE = os.path.expanduser("~/ai/budget.json")
logger = logging.getLogger("common.budget")

class BudgetTracker:
    def __init__(self, daily_limit_usd: float = 1.00):
        self.daily_limit_usd = daily_limit_usd
        self.current_spend = 0.0
        self.last_reset = time.time()
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
        self._save()

    def record_usage(self, provider: str, cost_usd: float):
        """Record a successful API call cost."""
        self.current_spend += cost_usd
        self._save()
        if self.current_spend > self.daily_limit_usd * 0.9:
            logger.warning(f"⚠️ Budget Alert: ${self.current_spend:.4f} / ${self.daily_limit_usd:.2f}")

    def check_budget(self, estimated_cost: float = 0.0) -> bool:
        """Returns True if request is allowed, False if budget exceeded."""
        if self.current_spend + estimated_cost > self.daily_limit_usd:
            logger.error(f"⛔ Budget Blocked: Request would exceed limit (${self.current_spend:.4f} >= ${self.daily_limit_usd:.2f})")
            return False
        return True

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Rough estimation of cost."""
        # Pricing Table (Apr 2024 / Dec 2025 Estimates)
        # H100 Serverless: ~$0.003 - $0.005 per 1k tokens? No, usually per second.
        # But we track tokens as proxy.
        
        rate_in = 0.0
        rate_out = 0.0
        
        if "gpt-4o" in model:
            rate_in = 5.00 / 1_000_000
            rate_out = 15.00 / 1_000_000
        elif "gpt-3.5" in model or "gpt-4o-mini" in model:
            rate_in = 0.50 / 1_000_000
            rate_out = 1.50 / 1_000_000
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
             
        return (input_tokens * rate_in) + (output_tokens * rate_out)

# Singleton
_tracker = None
def get_budget_tracker() -> BudgetTracker:
    global _tracker
    if _tracker is None:
        _tracker = BudgetTracker()
    return _tracker
