"""
Logging utilities for structured JSON event logging.

Provides consistent JSON event logging across all system components.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger("logging_utils")

@asynccontextmanager
async def log_time(operation_name: str, level=logging.DEBUG, logger_override=None):
    """
    Context manager to log the execution time of a block of code.
    """
    t0 = time.time()
    try:
        yield
    finally:
        duration = time.time() - t0
        target_logger = logger_override or logger
        target_logger.log(level, f"PERF: {operation_name} completed in {duration:.4f}s")


def log_json_event(event: str, request_id: Optional[str] = None, **fields: Any) -> None:
    """
    Emit a JSON_EVENT line for machine parsing.
    
    Args:
        event: Event name/type
        request_id: Optional request ID for request tracking
        **fields: Additional fields to include in the event
    """
    try:
        payload = {"event": event, **fields}
        if request_id:
            payload["request_id"] = request_id
        logger.info("JSON_EVENT: %s", json.dumps(payload, ensure_ascii=False))
    except Exception:
        logger.debug("failed to log JSON_EVENT for %s", event)


# Error classification and debugging helpers
ERROR_CATEGORIES = {
    "api_key": "Check API keys in providers.env",
    "network": "Check network connectivity and service availability",
    "timeout": "Check service load and timeout configurations",
    "circuit_breaker": "Service temporarily unavailable - check circuit breaker status",
    "model_unavailable": "Check model availability and Ollama service",
    "rate_limit": "API rate limit exceeded - implement backoff strategy",
    "validation": "Check input data format and requirements",
    "permission": "Check authentication and authorization",
    "resource": "Check system resources (memory, disk, CPU)",
    "configuration": "Check configuration files and environment variables"
}

# Standardized error codes for consistent error handling
ERROR_CODES = {
    # API and Authentication Errors
    "AUTH_INVALID_KEY": {"message": "Invalid or missing API key", "action": "Check providers.env file and API key validity"},
    "AUTH_RATE_LIMITED": {"message": "API rate limit exceeded", "action": "Implement exponential backoff or upgrade API tier"},
    "AUTH_PERMISSION_DENIED": {"message": "Insufficient permissions", "action": "Check API key permissions and account status"},

    # Network and Connectivity Errors
    "NETWORK_CONNECTION_FAILED": {"message": "Cannot connect to service", "action": "Check network connectivity, firewall, and service status"},
    "NETWORK_TIMEOUT": {"message": "Request timed out", "action": "Check service load, increase timeout, or retry request"},
    "NETWORK_DNS_FAILED": {"message": "DNS resolution failed", "action": "Check DNS configuration and network settings"},

    # Model and Service Errors
    "MODEL_NOT_FOUND": {"message": "Requested model not available", "action": "Check model name spelling and availability"},
    "MODEL_OVERLOADED": {"message": "Model service overloaded", "action": "Wait and retry, or use different model"},
    "MODEL_CIRCUIT_OPEN": {"message": "Model temporarily unavailable", "action": "Wait for auto-recovery or check circuit breaker status"},

    # Data and Validation Errors
    "VALIDATION_INVALID_FORMAT": {"message": "Invalid data format", "action": "Check input data structure and required fields"},
    "VALIDATION_SIZE_EXCEEDED": {"message": "Data size limit exceeded", "action": "Reduce input size or check service limits"},
    "VALIDATION_MISSING_REQUIRED": {"message": "Required field missing", "action": "Provide all required fields in request"},

    # System and Resource Errors
    "SYSTEM_OUT_OF_MEMORY": {"message": "Insufficient memory", "action": "Check system memory usage and restart if needed"},
    "SYSTEM_DISK_FULL": {"message": "Disk space exhausted", "action": "Free up disk space or check storage limits"},
    "SYSTEM_RESOURCE_EXHAUSTED": {"message": "System resources exhausted", "action": "Check CPU, memory, and other system resources"},

    # Configuration Errors
    "CONFIG_FILE_MISSING": {"message": "Configuration file not found", "action": "Check file paths and create missing configuration files"},
    "CONFIG_INVALID_FORMAT": {"message": "Invalid configuration format", "action": "Validate configuration file syntax and structure"},
    "CONFIG_MISSING_KEY": {"message": "Required configuration missing", "action": "Add missing configuration keys or use defaults"}
}

def classify_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Classify an error and provide debugging guidance.

    Args:
        error: The exception that occurred
        context: Additional context about the operation

    Returns:
        Dict with category, action, and severity
    """
    error_msg = str(error).lower()
    error_type = type(error).__name__

    # API Key errors
    if any(keyword in error_msg for keyword in ["unauthorized", "invalid api key", "authentication failed"]):
        return {
            "category": "api_key",
            "action": ERROR_CATEGORIES["api_key"],
            "severity": "high",
            "checklist": ["Verify providers.env exists", "Check API key format", "Confirm service access"]
        }

    # Network/Connectivity errors
    if any(keyword in error_msg for keyword in ["connection refused", "connection reset", "network", "unreachable"]):
        return {
            "category": "network",
            "action": ERROR_CATEGORIES["network"],
            "severity": "medium",
            "checklist": ["Check service health", "Verify network connectivity", "Check firewall rules"]
        }

    # Timeout errors
    if "timeout" in error_msg or error_type == "TimeoutError":
        return {
            "category": "timeout",
            "action": ERROR_CATEGORIES["timeout"],
            "severity": "medium",
            "checklist": ["Check service load", "Review timeout settings", "Monitor resource usage"]
        }

    # Circuit breaker errors
    if "circuit" in error_msg.lower() or "breaker" in error_msg.lower():
        return {
            "category": "circuit_breaker",
            "action": ERROR_CATEGORIES["circuit_breaker"],
            "severity": "low",
            "checklist": ["Wait for auto-recovery", "Check service health", "Monitor error rates"]
        }

    # Model availability
    if any(keyword in error_msg for keyword in ["model not found", "model unavailable", "ollama"]):
        return {
            "category": "model_unavailable",
            "action": ERROR_CATEGORIES["model_unavailable"],
            "severity": "high",
            "checklist": ["Check Ollama service status", "Verify model is pulled", "Check model name spelling"]
        }

    # Rate limiting
    if any(keyword in error_msg for keyword in ["rate limit", "too many requests", "429"]):
        return {
            "category": "rate_limit",
            "action": ERROR_CATEGORIES["rate_limit"],
            "severity": "medium",
            "checklist": ["Implement exponential backoff", "Check API usage limits", "Consider upgrading plan"]
        }

    # Validation errors
    if any(keyword in error_msg for keyword in ["validation", "invalid", "malformed", "format"]):
        return {
            "category": "validation",
            "action": ERROR_CATEGORIES["validation"],
            "severity": "medium",
            "checklist": ["Check input data format", "Validate required fields", "Review API documentation"]
        }

    # Default classification
    return {
        "category": "unknown",
        "action": "Check logs for additional context and review error details",
        "severity": "medium",
        "checklist": ["Review error message", "Check system logs", "Monitor for patterns"]
    }


def log_error_with_context(error: Exception, operation: str, request_id: Optional[str] = None,
                          context: Dict[str, Any] = None, logger_instance=None) -> None:
    """
    Log an error with actionable debugging context.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
        request_id: Request ID for correlation
        context: Additional context (model, service, etc.)
        logger_instance: Logger to use (defaults to module logger)
    """
    target_logger = logger_instance or logger
    context = context or {}

    # Classify the error
    error_info = classify_error(error, context)

    # Build structured error message
    error_parts = [
        f"ERROR [{error_info['category'].upper()}]: {operation} failed",
        f"ACTION: {error_info['action']}",
        f"SEVERITY: {error_info['severity']}"
    ]

    if request_id:
        error_parts.insert(0, f"REQ [{request_id}]")

    # Add context information
    context_items = []
    if "model" in context:
        context_items.append(f"MODEL: {context['model']}")
    if "service" in context:
        context_items.append(f"SERVICE: {context['service']}")
    if "endpoint" in context:
        context_items.append(f"ENDPOINT: {context['endpoint']}")

    if context_items:
        error_parts.append(f"CONTEXT: {' | '.join(context_items)}")

    # Add checklist
    if error_info.get("checklist"):
        error_parts.append(f"CHECKLIST: {' | '.join(error_info['checklist'])}")

    # Log the structured error
    full_message = " | ".join(error_parts)
    target_logger.error(f"{full_message} | DETAILS: {str(error)}", exc_info=True)

    # Capture debug snapshot if in debug mode
    log_debug_snapshot(request_id, operation)

    # Also emit as structured event for monitoring
    event_data = {
        "operation": operation,
        "error_category": error_info["category"],
        "error_severity": error_info["severity"],
        "error_type": type(error).__name__,
        "action_required": error_info["action"],
        **context
    }

    log_json_event("error_occurred", request_id, **event_data)


def capture_debug_snapshot() -> Dict[str, Any]:
    """
    Capture comprehensive system state for debugging.

    Returns:
        Dict containing system state, health metrics, and configuration
    """
    try:
        # Import here to avoid circular imports
        from agent_runner.agent_runner import get_shared_state, get_shared_engine

        state = get_shared_state()
        engine = get_shared_engine()

        snapshot = {
            "timestamp": time.time(),
            "system_info": {
                "platform": "unknown",  # Would need platform module
                "python_version": "unknown",  # Would need sys module
                "uptime": time.time() - getattr(state, 'started_at', time.time())
            }
        }

        # State information
        if state:
            snapshot["state"] = {
                "internet_available": getattr(state, 'internet_available', False),
                "request_count": getattr(state, 'request_count', 0),
                "error_count": getattr(state, 'error_count', 0),
                "last_error": getattr(state, 'last_error', ''),
                "active_client_id": getattr(state, 'active_client_id', None),
                "quality_tier": getattr(state, 'quality_tier', None)
            }

            # Circuit breaker status
            if hasattr(state, 'mcp_circuit_breaker'):
                cb_status = state.mcp_circuit_breaker.get_status()
                snapshot["circuit_breakers"] = cb_status

        # Engine information
        if engine and hasattr(engine, 'state'):
            snapshot["engine"] = {
                "max_tool_steps": getattr(engine.state, 'max_tool_steps', 0),
                "context_prune_limit": getattr(engine.state, 'context_prune_limit', 0),
                "agent_model": getattr(engine.state, 'agent_model', ''),
                "fallback_model": getattr(engine.state, 'fallback_model', '')
            }

        # Recent health metrics (if available)
        try:
            from agent_runner.health_monitor import get_recent_health_metrics
            snapshot["recent_health"] = get_recent_health_metrics()
        except:
            snapshot["recent_health"] = "unavailable"

        return snapshot

    except Exception as e:
        return {"error": f"Failed to capture debug snapshot: {str(e)}"}


def log_debug_snapshot(request_id: Optional[str] = None, operation: str = "unknown") -> None:
    """
    Log a comprehensive debug snapshot when in debug mode.

    Args:
        request_id: Request ID for correlation
        operation: Operation that triggered the snapshot
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return  # Only capture in debug mode

    try:
        snapshot = capture_debug_snapshot()
        snapshot["operation"] = operation

        # Log as structured JSON for easy parsing
        logger.debug(f"DEBUG_SNAPSHOT: {json.dumps(snapshot, indent=2, default=str)}")

        # Also emit as structured event
        log_json_event("debug_snapshot", request_id, **snapshot)

    except Exception as e:
        logger.debug(f"Failed to capture debug snapshot: {e}")


# Structured log templates for consistent logging
LOG_TEMPLATES = {
    "model_call": "MODEL_CALL: {model} | LATENCY: {latency:.2f}s | TOKENS: {tokens} | STATUS: {status} | REQ: {request_id}",
    "circuit_break": "CIRCUIT_BREAK: {service} | STATE: {state} | FAILURES: {failures}/{threshold} | ACTION: {action}",
    "health_check": "HEALTH_CHECK: {service} | STATUS: {status} | LATENCY: {latency:.2f}s | ERRORS: {error_count}",
    "performance_alert": "PERF_ALERT: {operation} took {duration:.2f}s (> {threshold}s threshold) | ACTION: {action}",
    "request_start": "REQ_START [{request_id}]: {operation} | MODEL: {model} | USER: {user_agent}",
    "request_complete": "REQ_COMPLETE [{request_id}]: {operation} | DURATION: {duration:.2f}s | STATUS: {status}",
    "error_actionable": "ERROR [{category}]: {operation} failed | ACTION: {action} | SEVERITY: {severity} | REQ: {request_id}"
}

def log_structured(template_name: str, request_id: Optional[str] = None, **kwargs) -> None:
    """
    Log using a structured template for consistency.

    Args:
        template_name: Name of template from LOG_TEMPLATES
        request_id: Request ID for correlation
        **kwargs: Values to substitute in template
    """
    if template_name not in LOG_TEMPLATES:
        logger.warning(f"Unknown log template: {template_name}")
        return

    template = LOG_TEMPLATES[template_name]
    try:
        message = template.format(**kwargs)
        logger.info(message)

        # Also emit as structured event
        event_data = {"template": template_name, **kwargs}
        log_json_event(f"log_{template_name}", request_id, **event_data)

    except KeyError as e:
        logger.warning(f"Missing required field for template {template_name}: {e}")
    except Exception as e:
        logger.warning(f"Failed to format log template {template_name}: {e}")














