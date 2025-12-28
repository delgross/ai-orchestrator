import time
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger("common.circuit_breaker")

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocked
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """
    Standard Circuit Breaker implementation for services and MCP servers.
    """
    def __init__(
        self,
        name: str,
        threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_tests: int = 1
    ):
        self.name = name
        self.threshold = threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_tests = half_open_max_tests
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0.0
        self.disabled_until = 0.0
        self.half_open_tests = 0
        self.total_failures = 0
        self.total_successes = 0

    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        now = time.time()
        
        if self.state == CircuitState.OPEN:
            if now >= self.disabled_until:
                # Transition to half-open to test recovery
                logger.info(f"Circuit Breaker '{self.name}': Transitioning to HALF_OPEN for recovery test")
                self.state = CircuitState.HALF_OPEN
                self.half_open_tests = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_tests >= self.half_open_max_tests:
                # Only allow a limited number of tests in half-open state
                return False
            return True
            
        return self.state == CircuitState.CLOSED

    def record_success(self):
        """Record a successful request."""
        self.total_successes += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Successful test in half-open state - fully recover
            logger.info(f"Circuit Breaker '{self.name}': Recovery successful, transitioning to CLOSED")
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.half_open_tests = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failures on success if we were tracking partial failures
            if self.failures > 0:
                self.failures = 0

    def record_failure(self, weight: int = 1):
        """
        Record a failed request.
        Weight can be > 1 for critical failures (e.g. process crash).
        """
        self.total_failures += 1
        self.failures += weight
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test - move back to open with longer timeout
            logger.warning(f"Circuit Breaker '{self.name}': Recovery test failed, returning to OPEN")
            self.state = CircuitState.OPEN
            self.disabled_until = time.time() + (self.recovery_timeout * 2) # Backoff
            self.half_open_tests = 0
            
        elif self.state == CircuitState.CLOSED:
            if self.failures >= self.threshold:
                logger.error(f"Circuit Breaker '{self.name}': Threshold {self.threshold} reached, transitioning to OPEN")
                self.state = CircuitState.OPEN
                self.disabled_until = time.time() + self.recovery_timeout

    def increment_test_count(self):
        """Track tests in half-open state."""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_tests += 1

    def reset(self):
        """Manually reset the circuit breaker to CLOSED state."""
        logger.info(f"Circuit Breaker '{self.name}': Manually reset to CLOSED")
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.half_open_tests = 0
        self.disabled_until = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for observability/API."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self.failures,
            "last_failure_time": self.last_failure_time,
            "disabled_until": self.disabled_until,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "seconds_remaining": max(0, self.disabled_until - time.time()) if self.state == CircuitState.OPEN else 0
        }

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    def __init__(self, default_threshold: int = 5, default_timeout: float = 60.0):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.default_threshold = default_threshold
        self.default_timeout = default_timeout

    def get_breaker(self, name: str) -> CircuitBreaker:
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                threshold=self.default_threshold,
                recovery_timeout=self.default_timeout
            )
        return self.breakers[name]

    def record_success(self, name: str):
        self.get_breaker(name).record_success()

    def record_failure(self, name: str, weight: int = 1):
        self.get_breaker(name).record_failure(weight)

    def is_allowed(self, name: str) -> bool:
        return self.get_breaker(name).is_allowed()

    def reset(self, name: str):
        """Reset a specific circuit breaker."""
        if name in self.breakers:
            self.breakers[name].reset()

    def reset_all(self):
        """Reset all managed circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()

    def get_status(self) -> Dict[str, Dict[str, Any]]:
        return {name: breaker.to_dict() for name, breaker in self.breakers.items()}
