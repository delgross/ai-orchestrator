import time
import logging
from enum import Enum
from typing import Dict, Any

# from common.notifications import notify_health, notify_info

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
        self.last_error = None
        self.last_error_time = 0.0
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
            from common.notifications import notify_info
            notify_info(
                f"Service Recovered: {self.name}",
                f"Circuit breaker '{self.name}' has recovered and is now CLOSED.",
                source="CircuitBreaker"
            )
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.half_open_tests = 0
            
            # [Phase 25c] Auto-Reset Heuristic:
            # If we just recovered from a failure, clear the error history so the
            # dashboard doesn't show "100% Error Rate" based on the downtime we just fixed.
            try:
                from common.observability import get_observability
                obs = get_observability()
                # Run this async without blocking
                import asyncio
                # We need to ensure there is a running loop, or just skip if sync context (rare)
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(obs.reset_history(['errors', 'health']))
                    logger.info(f"Circuit Breaker '{self.name}': Auto-triggering Observability Reset (Heuristic)")
                except RuntimeError:
                    pass 
            except ImportError:
                pass

        elif self.state == CircuitState.CLOSED:
            # Reset failures on success if we were tracking partial failures
            if self.failures > 0:
                self.failures = 0

    def record_failure(self, weight: int = 1, error: Any = None):
        """
        Record a failed request.
        Weight can be > 1 for critical failures (e.g. process crash).
        """
        self.total_failures += 1
        self.failures += weight
        self.last_failure_time = time.time()
        
        if error:
            self.last_error = str(error)
            self.last_error_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery test - move back to open with longer timeout
            logger.warning(f"Circuit Breaker '{self.name}': Recovery test failed, returning to OPEN. Error: {self.last_error}")
            self.state = CircuitState.OPEN
            self.disabled_until = time.time() + (self.recovery_timeout * 2) # Backoff
            self.half_open_tests = 0
            
            # Track the failed recovery attempt
            from common.unified_tracking import track_event, EventSeverity, EventCategory
            track_event(
                event="circuit_breaker_recovery_failed",
                severity=EventSeverity.HIGH,
                category=EventCategory.HEALTH,
                message=f"Service '{self.name}' failed recovery check.",
                metadata={
                    "circuit": self.name, 
                    "error": self.last_error,
                    "next_retry_seconds": self.recovery_timeout * 2
                }
            )
            
        elif self.state == CircuitState.CLOSED:
            if self.failures >= self.threshold:
                logger.error(f"Circuit Breaker '{self.name}': Threshold {self.threshold} reached, transitioning to OPEN. Last Error: {self.last_error}")
                
                # Use Unified Tracker for the alert
                from common.unified_tracking import track_event, EventSeverity, EventCategory
                track_event(
                    event="circuit_breaker_tripped",
                    severity=EventSeverity.CRITICAL,  # Critical because a service is now down
                    category=EventCategory.HEALTH,
                    message=f"Service Suspended: {self.name}",
                    metadata={
                        "circuit": self.name,
                        "threshold": self.threshold,
                        "failures": self.failures,
                        "last_error": self.last_error
                    }
                )
                
                self.state = CircuitState.OPEN
                self.state = CircuitState.OPEN
                self.disabled_until = time.time() + self.recovery_timeout
            else:
                # [Fix] Report individual failures before tripping
                from common.unified_tracking import track_event, EventSeverity, EventCategory
                track_event(
                    event="circuit_breaker_failure",
                    severity=EventSeverity.DEBUG, # Hidden from user logs, debugging only
                    category=EventCategory.HEALTH,
                    message=f"Service Glitch: {self.name} ({self.failures}/{self.threshold})",
                    metadata={
                        "circuit": self.name,
                        "failures": self.failures,
                        "threshold": self.threshold,
                        "error": self.last_error
                    }
                )

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
            "last_error": self.last_error,
            "last_error_time": self.last_error_time,
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

    def record_failure(self, name: str, weight: int = 1, error: Any = None):
        self.get_breaker(name).record_failure(weight, error)

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

    def detect_system_lockdown(self, critical_services: list[str]) -> bool:
        """
        Returns True if ALL specified critical services are in OPEN state.
        This indicates a potential dependency deadlock where systems cannot recover
        because they are waiting for each other.
        """
        if not critical_services or not self.breakers:
            return False
            
        down_count = 0
        monitored_count = 0 
        
        for name in critical_services:
            if name in self.breakers:
                monitored_count += 1
                if self.breakers[name].state == CircuitState.OPEN:
                    down_count += 1
        
        # Lockout only if we are actually monitoring these services and ALL are down
        return monitored_count > 0 and down_count == monitored_count

    def emergency_release_lockdown(self, critical_services: list[str]):
        """
        Force resets critical breakers to attempt a 'Global Reset Propagation'.
        Used when a deadlock is detected.
        """
        logger.warning(f"🚨 DEADLOCK MITIGATION: Forcing reset of {critical_services}")
        for name in critical_services:
            if name in self.breakers:
                self.breakers[name].reset()
                # Record this special event
                from common.unified_tracking import track_event, EventSeverity, EventCategory
                track_event(
                    event="circuit_breaker_deadlock_release",
                    severity=EventSeverity.CRITICAL,
                    category=EventCategory.SYSTEM,
                    message=f"Forced reset of '{name}' to break system deadlock.",
                    metadata={"service": name}
                )
