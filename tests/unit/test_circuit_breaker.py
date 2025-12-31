import pytest
import time
from common.circuit_breaker import CircuitBreakerRegistry, CircuitState

def test_circuit_breaker_transitions():
    registry = CircuitBreakerRegistry(default_threshold=2, default_timeout=1.0)
    breaker = registry.get_breaker("test_service")
    
    # 1. Closed initially
    assert breaker.state == CircuitState.CLOSED
    assert breaker.is_allowed()
    
    # 2. Record failures (Threshold 2)
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED  # 1/2
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN    # 2/2
    assert not breaker.is_allowed()
    
    # 3. Timeout Recovery
    # We can't easily mock time.time in the class without injection, 
    # so we manually manipulate the breaker's internal state for testing speed.
    breaker.disabled_until = 0 # Force ready
    
    # is_allowed() should trigger transition to HALF_OPEN
    assert breaker.is_allowed() 
    assert breaker.state == CircuitState.HALF_OPEN
    
    # 4. Success closes it
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failures == 0

def test_deadlock_detection():
    registry = CircuitBreakerRegistry(default_threshold=1)
    
    # Init breakers
    registry.get_breaker("service_a")
    registry.get_breaker("service_b")
    registry.get_breaker("service_c") # Non-critical
    
    criticals = ["service_a", "service_b"]
    
    # 1. Healthy
    assert not registry.detect_system_lockdown(criticals)
    
    # 2. Partial Failure
    registry.record_failure("service_a")
    assert registry.get_breaker("service_a").state == CircuitState.OPEN
    assert not registry.detect_system_lockdown(criticals)  # Only A is down
    
    # 3. Total Lockout
    registry.record_failure("service_b")
    assert registry.get_breaker("service_b").state == CircuitState.OPEN
    
    assert registry.detect_system_lockdown(criticals) # Both A and B are down
    
    # 4. Mitigation
    registry.emergency_release_lockdown(criticals)
    assert registry.get_breaker("service_a").state == CircuitState.CLOSED
    assert registry.get_breaker("service_b").state == CircuitState.CLOSED
    assert not registry.detect_system_lockdown(criticals)
