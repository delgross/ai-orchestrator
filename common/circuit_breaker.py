import time
import logging
import asyncio
from enum import Enum
from typing import Dict, Any, Optional

# Note: notify_health and notify_info imports removed - using inline import if needed

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
        half_open_max_tests: int = 1,
        max_recovery_attempts: int = 10,
        max_backoff: float = 300.0
    ):
        self.name = name
        self.threshold = threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_tests = half_open_max_tests
        self.max_recovery_attempts = max_recovery_attempts
        self.max_backoff = max_backoff
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0.0
        self.last_error = None
        self.last_error_time = 0.0
        self.disabled_until = 0.0
        self.half_open_tests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.recovery_attempts = 0  # Track recovery attempts (resets on successful recovery)
        self.permanently_disabled = False  # True after max_recovery_attempts reached
        
        # Debounced DB update mechanism
        self._pending_db_update_task: Optional[asyncio.Task] = None
        self._db_update_delay = 5.0  # 5 second delay for debouncing

    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        # Permanently disabled servers are never allowed
        if self.permanently_disabled:
            return False
        
        now = time.time()
        
        if self.state == CircuitState.OPEN:
            if now >= self.disabled_until:
                # Transition to half-open to test recovery
                logger.info(f"Circuit Breaker '{self.name}': Transitioning to HALF_OPEN for recovery test (attempt {self.recovery_attempts + 1}/{self.max_recovery_attempts})")
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

    async def _update_database_state(self, enabled: bool, disabled_reason: Optional[str] = None, immediate: bool = False):
        """
        Update database state for this circuit breaker's server.
        Uses debouncing unless immediate=True.
        
        Args:
            enabled: Whether server should be enabled
            disabled_reason: Reason for being disabled (None if enabled)
            immediate: If True, update immediately without debouncing
        """
        try:
            from agent_runner.agent_runner import get_shared_state
            state = get_shared_state()
            if not state or not hasattr(state, 'mcp_servers') or self.name not in state.mcp_servers:
                return  # Not an MCP server or state not available
            
            # Check if update is needed (conditional update)
            if not immediate:
                try:
                    if hasattr(state, 'memory') and state.memory and state.memory.initialized:
                        # Check current DB state
                        from agent_runner.db_utils import run_query
                        query = f"SELECT enabled, disabled_reason FROM mcp_server WHERE name = '{self.name}'"
                        result = await run_query(state, query)
                        if result and len(result) > 0:
                            current_enabled = result[0].get("enabled", True)
                            current_reason = result[0].get("disabled_reason")
                            # Skip update if already matches
                            if current_enabled == enabled and current_reason == disabled_reason:
                                logger.debug(f"Circuit Breaker '{self.name}': DB state already matches, skipping update")
                                return
                except Exception as e:
                    logger.debug(f"Circuit Breaker '{self.name}': Could not check DB state: {e}")
                    # Continue with update if check fails
            
            # Update runtime state
            state.mcp_servers[self.name]["enabled"] = enabled
            if disabled_reason:
                state.mcp_servers[self.name]["disabled_reason"] = disabled_reason
            elif "disabled_reason" in state.mcp_servers[self.name]:
                del state.mcp_servers[self.name]["disabled_reason"]
            
            # Update database via config_manager
            if hasattr(state, 'config_manager') and state.config_manager:
                config = state.mcp_servers[self.name].copy()
                await state.config_manager.update_mcp_server(self.name, config)
                logger.info(f"Circuit Breaker '{self.name}': Updated database - enabled={enabled}, reason={disabled_reason}")
        except Exception as e:
            logger.warning(f"Circuit Breaker '{self.name}': Failed to update database: {e}")
            # Don't raise - database update failure shouldn't break circuit breaker logic

    async def _debounced_db_update(self, enabled: bool, disabled_reason: Optional[str] = None):
        """
        Schedule a debounced database update. Cancels any pending update for this breaker.
        """
        # Cancel previous pending update if exists
        if self._pending_db_update_task and not self._pending_db_update_task.done():
            self._pending_db_update_task.cancel()
            try:
                await self._pending_db_update_task
            except asyncio.CancelledError:
                pass
        
        # Schedule new update
        async def _delayed_update():
            try:
                await asyncio.sleep(self._db_update_delay)
                # Check if state is still what we want to update
                # (circuit breaker might have changed state during delay)
                if self.state == CircuitState.OPEN and not enabled:
                    # Still OPEN, update DB
                    await self._update_database_state(enabled, disabled_reason, immediate=True)
                elif self.state == CircuitState.CLOSED and enabled:
                    # Still CLOSED, update DB
                    await self._update_database_state(enabled, disabled_reason, immediate=True)
                # If state changed, don't update (new state change will schedule its own update)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.warning(f"Circuit Breaker '{self.name}': Debounced DB update failed: {e}")
        
        try:
            loop = asyncio.get_running_loop()
            self._pending_db_update_task = loop.create_task(_delayed_update())
        except RuntimeError:
            # No event loop, update immediately
            await self._update_database_state(enabled, disabled_reason, immediate=True)

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
            # Reset recovery attempts on successful recovery (fresh start)
            self.recovery_attempts = 0
            self.permanently_disabled = False
            
            # Auto-re-enable in database after successful recovery
            # Only if disabled_reason was 'circuit_breaker_opened' (not user_disabled or permanently_disabled)
            try:
                from agent_runner.agent_runner import get_shared_state
                state = get_shared_state()
                if state and hasattr(state, 'mcp_servers') and self.name in state.mcp_servers:
                    current_reason = state.mcp_servers[self.name].get("disabled_reason")
                    # Only auto-re-enable if it was disabled by circuit breaker
                    if current_reason == "circuit_breaker_opened":
                        # Schedule async update (fire-and-forget)
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(self._update_database_state(True, None, immediate=True))
                            logger.info(f"Circuit Breaker '{self.name}': Auto-re-enabling in database after successful recovery")
                        except RuntimeError:
                            # No event loop, can't schedule async update
                            logger.debug(f"Circuit Breaker '{self.name}': No event loop for async DB update")
            except Exception as e:
                logger.debug(f"Circuit Breaker '{self.name}': Could not auto-re-enable in DB: {e}")
            
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
            # Failed during recovery test - increment recovery attempts
            self.recovery_attempts += 1
            logger.warning(f"Circuit Breaker '{self.name}': Recovery test failed (attempt {self.recovery_attempts}/{self.max_recovery_attempts}), returning to OPEN. Error: {self.last_error}")
            
            # Check if we've exceeded max recovery attempts
            if self.recovery_attempts >= self.max_recovery_attempts:
                # Permanently disable - max recovery attempts reached
                self.permanently_disabled = True
                self.state = CircuitState.OPEN
                self.disabled_until = float('inf')  # Never allow recovery attempts
                self.half_open_tests = 0
                
                logger.error(f"Circuit Breaker '{self.name}': Max recovery attempts ({self.max_recovery_attempts}) reached. Permanently disabled. Requires manual intervention.")
                
                # CRITICAL notification for permanent disable
                from common.unified_tracking import track_event, EventSeverity, EventCategory
                track_event(
                    event="circuit_breaker_permanently_disabled",
                    severity=EventSeverity.CRITICAL,
                    category=EventCategory.HEALTH,
                    message=f"Service '{self.name}' permanently disabled after {self.max_recovery_attempts} failed recovery attempts. Requires manual intervention.",
                    metadata={
                        "circuit": self.name,
                        "recovery_attempts": self.recovery_attempts,
                        "max_recovery_attempts": self.max_recovery_attempts,
                        "error": self.last_error
                    }
                )
                
                # Update database immediately (critical state change, no debouncing)
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self._update_database_state(
                        False, 
                        "permanently_disabled",
                        immediate=True
                    ))
                except RuntimeError:
                    # No event loop, try sync update (won't work but won't break)
                    logger.debug(f"Circuit Breaker '{self.name}': No event loop for DB update")
                
                # Also disable server in runtime if it's an MCP server
                try:
                    from agent_runner.agent_runner import get_shared_state
                    state = get_shared_state()
                    if state and hasattr(state, 'mcp_servers') and self.name in state.mcp_servers:
                        state.mcp_servers[self.name]["enabled"] = False
                        state.mcp_servers[self.name]["disabled_reason"] = "permanently_disabled"
                        logger.warning(f"MCP Server '{self.name}' permanently disabled in runtime. Requires manual intervention.")
                except Exception as e:
                    logger.debug(f"Could not permanently disable MCP server '{self.name}': {e}")
            else:
                # Continue with exponential backoff (capped at max_backoff)
                # Backoff: recovery_timeout * 2^(attempts-1), capped at max_backoff
                # Attempt 1: recovery_timeout * 2^0 = recovery_timeout (60s)
                # Attempt 2: recovery_timeout * 2^1 = recovery_timeout * 2 (120s)
                # Attempt 3: recovery_timeout * 2^2 = recovery_timeout * 4 (240s)
                # Attempt 4+: capped at max_backoff (300s)
                backoff_multiplier = min(2 ** (self.recovery_attempts - 1), self.max_backoff / self.recovery_timeout)
                backoff_seconds = min(self.recovery_timeout * backoff_multiplier, self.max_backoff)
                
                self.state = CircuitState.OPEN
                self.disabled_until = time.time() + backoff_seconds
                self.half_open_tests = 0
                
                # Schedule debounced DB update (circuit breaker opened)
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self._debounced_db_update(False, "circuit_breaker_opened"))
                except RuntimeError:
                    logger.debug(f"Circuit Breaker '{self.name}': No event loop for debounced DB update")
                
                # Track the failed recovery attempt (HIGH severity)
                from common.unified_tracking import track_event, EventSeverity, EventCategory
                track_event(
                    event="circuit_breaker_recovery_failed",
                    severity=EventSeverity.HIGH,
                    category=EventCategory.HEALTH,
                    message=f"Service '{self.name}' failed recovery check (attempt {self.recovery_attempts}/{self.max_recovery_attempts}).",
                    metadata={
                        "circuit": self.name, 
                        "error": self.last_error,
                        "recovery_attempts": self.recovery_attempts,
                        "max_recovery_attempts": self.max_recovery_attempts,
                        "next_retry_seconds": backoff_seconds
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
                self.disabled_until = time.time() + self.recovery_timeout
                
                # Schedule debounced DB update (circuit breaker opened)
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self._debounced_db_update(False, "circuit_breaker_opened"))
                except RuntimeError:
                    logger.debug(f"Circuit Breaker '{self.name}': No event loop for debounced DB update")
                
                # [NEW] Automatically disable server in runtime (but keep DB config)
                # This removes it from available servers list while preserving database details
                try:
                    # Import here to avoid circular dependency
                    from agent_runner.agent_runner import get_shared_state
                    state = get_shared_state()
                    if state and hasattr(state, 'mcp_servers') and self.name in state.mcp_servers:
                        # Disable in runtime immediately
                        state.mcp_servers[self.name]["enabled"] = False
                        state.mcp_servers[self.name]["disabled_reason"] = "circuit_breaker_opened"
                        logger.warning(f"MCP Server '{self.name}' automatically disabled in runtime due to circuit breaker.")
                        
                        # Remove from tool cache so tools aren't available
                        from agent_runner.service_registry import ServiceRegistry
                        try:
                            engine = ServiceRegistry.get_engine()
                            if hasattr(engine, 'executor') and hasattr(engine.executor, 'mcp_tool_cache'):
                                if self.name in engine.executor.mcp_tool_cache:
                                    del engine.executor.mcp_tool_cache[self.name]
                                    logger.info(f"Removed '{self.name}' from tool cache. Server can be re-enabled later.")
                        except (RuntimeError, AttributeError):
                            pass  # Engine not available yet
                        
                        # Report to system
                        track_event(
                            event="mcp_server_auto_disabled",
                            severity=EventSeverity.HIGH,
                            category=EventCategory.MCP,
                            message=f"MCP server '{self.name}' automatically disabled due to repeated failures. Database config preserved.",
                            metadata={
                                "server": self.name,
                                "reason": "circuit_breaker_opened",
                                "failures": self.failures,
                                "error": self.last_error
                            }
                        )
                except Exception as e:
                    logger.debug(f"Could not auto-disable MCP server '{self.name}': {e}")
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
        self.recovery_attempts = 0
        self.permanently_disabled = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for observability/API."""
        now = time.time()
        seconds_remaining = 0
        if self.state == CircuitState.OPEN:
            if self.permanently_disabled:
                seconds_remaining = -1  # Special value for permanently disabled
            else:
                seconds_remaining = max(0, self.disabled_until - now)
        
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
            "seconds_remaining": seconds_remaining,
            "recovery_attempts": self.recovery_attempts,
            "max_recovery_attempts": self.max_recovery_attempts,
            "permanently_disabled": self.permanently_disabled
        }

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers with memory caching."""
    def __init__(self, default_threshold: int = 5, default_timeout: float = 60.0, core_services: set = None):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.default_threshold = default_threshold
        self.default_timeout = default_timeout
        self.core_services = core_services or set()

        # Core service thresholds (higher tolerance for critical services)
        self.core_threshold = 10  # Core services need 10 failures (vs 5 for non-core)
        self.core_timeout = 30.0  # Core services recover faster (30s vs 60s)

        # Optimization: Memory cache for fast lookups
        self._allowed_cache: Dict[str, Tuple[bool, float]] = {}  # (is_allowed, timestamp)
        self._cache_ttl = 1.0  # Cache for 1 second

    def _is_core_service(self, name: str) -> bool:
        """Check if a service is a core service."""
        return name in self.core_services

    def get_breaker(self, name: str) -> CircuitBreaker:
        if name not in self.breakers:
            # Use higher thresholds for core services
            if self._is_core_service(name):
                threshold = self.core_threshold
                timeout = self.core_timeout
                logger.info(f"Circuit Breaker for core service '{name}': threshold={threshold}, timeout={timeout}s")
            else:
                threshold = self.default_threshold
                timeout = self.default_timeout
            
            self.breakers[name] = CircuitBreaker(
                name=name,
                threshold=threshold,
                recovery_timeout=timeout
            )
        return self.breakers[name]

    def record_success(self, name: str):
        self.get_breaker(name).record_success()
        # Invalidate cache since state changed
        self._allowed_cache.pop(name, None)

    def record_failure(self, name: str, weight: int = 1, error: Any = None):
        self.get_breaker(name).record_failure(weight, error)
        # Invalidate cache since state changed
        self._allowed_cache.pop(name, None)

    def is_allowed(self, name: str) -> bool:
        """Check if service is allowed with memory caching for performance."""
        now = time.time()

        # Check cache first (fast path)
        if name in self._allowed_cache:
            cached_result, cached_time = self._allowed_cache[name]
            if now - cached_time < self._cache_ttl:
                return cached_result

        # Cache miss - compute result (slower path)
        result = self.get_breaker(name).is_allowed()

        # Update cache
        self._allowed_cache[name] = (result, now)

        return result

    def reset(self, name: str):
        """Reset a specific circuit breaker."""
        if name in self.breakers:
            self.breakers[name].reset()

    def reset_all(self):
        """Reset all managed circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()
        # Clear cache since all states changed
        self._allowed_cache.clear()

    def clear_cache(self):
        """Clear the memory cache (useful for testing or manual invalidation)."""
        self._allowed_cache.clear()

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
