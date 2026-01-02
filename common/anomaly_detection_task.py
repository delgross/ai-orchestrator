"""
Anomaly Detection Background Task

Runs continuous anomaly detection and sends notifications when anomalies are detected.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

logger = logging.getLogger("anomaly_detection_task")


async def run_anomaly_detection(
    check_interval: float = 60.0,
    notify_on_anomaly: bool = True,
) -> None:
    """
    Run continuous anomaly detection.
    
    Args:
        check_interval: How often to check for anomalies (seconds)
        notify_on_anomaly: Whether to send notifications when anomalies detected
    """
    try:
        from common.observability import get_observability
        from common.anomaly_detector import AnomalySeverity
    except ImportError as e:
        logger.error(f"Failed to import observability/anomaly detector: {e}")
        return
    
    obs = get_observability()
    
    if not obs.anomaly_detector:
        logger.warning("Anomaly detector not available, skipping anomaly detection task")
        return
    
    logger.info(f"Starting anomaly detection task (check interval: {check_interval}s)")
    
    # Track last notification time per anomaly to avoid spam
    last_notification: Dict[str, float] = {}
    notification_cooldown = 300.0  # 5 minutes between notifications for same anomaly type
    
    while True:
        try:
            # Get current metrics (this also feeds metrics to detector)
            metrics = await obs.get_system_metrics()
            
            # Run anomaly detection
            anomalies = await obs.detect_anomalies()
            
            if anomalies:
                logger.info(f"Detected {len(anomalies)} anomaly/anomalies")
                
                # Send notifications for critical/warning anomalies
                if notify_on_anomaly:
                    for anomaly in anomalies:
                        # Only notify for WARNING and CRITICAL
                        if anomaly.severity in (AnomalySeverity.WARNING, AnomalySeverity.CRITICAL):
                            # Check cooldown
                            anomaly_key = f"{anomaly.metric_name}:{anomaly.severity.value}"
                            now = anomaly.timestamp
                            
                            if anomaly_key not in last_notification or (now - last_notification[anomaly_key]) > notification_cooldown:
                                await _notify_anomaly(anomaly, metrics)
                                last_notification[anomaly_key] = now
                        else:
                            # Log INFO anomalies but don't notify
                            logger.info(
                                f"Anomaly detected: {anomaly.metric_name} = {anomaly.current_value} "
                                f"(baseline: {anomaly.baseline_value}, deviation: {anomaly.deviation:.2f}σ)"
                            )

            # --- SQUEAKY WHEEL: Stuck Circuit Breaker Check ---
            try:
                # We attempt to load the local process state (Router or Agent)
                # This works if we are running inside the Router process
                from router.config import state as router_state
                from common.circuit_breaker import CircuitState
                import time
                
                for name, breaker in router_state.circuit_breakers.breakers.items():
                    if breaker.state == CircuitState.OPEN:
                        # If it has been failing for > 5 minutes (300s)
                        # We use 'last_failure_time' which updates on every probe failure
                        duration_open = time.time() - breaker.last_failure_time
                        
                        # However, last_failure_time resets on probe. 
                        # We want 'time since it FIRST opened'. 
                        # But breaker.disabled_until tells us when it *recovers*.
                        # Actually, if it's OPEN, it means it is currently broken. 
                        # If it is persistently OPEN, 'total_failures' keeps climbing.
                        
                        # Simple Logic: If it is OPEN, Alert every 30 seconds.
                        cb_key = f"cb_stuck:{name}"
                        now = time.time()
                        if cb_key not in last_notification or (now - last_notification[cb_key]) > 30:
                            logger.error(f"SQUEAKY WHEEL: Circuit '{name}' is STUCK OPEN.")
                            
                            # Send Toast
                            try:
                                from common.notifications import get_notification_manager, NotificationLevel
                                notifier = get_notification_manager()
                                notifier.notify(
                                    level=NotificationLevel.CRITICAL,
                                    title="System Functionality Limited",
                                    message=f"The '{name}' service has been unreachable for an extended period.",
                                    category="health",
                                    source="circuit_breaker_monitor"
                                )
                                last_notification[cb_key] = now
                            except Exception:
                                pass
            except ImportError:
                pass 
            # --------------------------------------------------
            
            # Wait before next check
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Error in anomaly detection task: {e}", exc_info=True)
            # Wait a bit before retrying
            await asyncio.sleep(check_interval)


async def _notify_anomaly(anomaly: Any, metrics: Any) -> None:
    """Send notification about detected anomaly."""
    # Write to blog first (always, regardless of notification system)
    try:
        from common.anomaly_blog import write_anomaly_to_blog
        blog_path = write_anomaly_to_blog(anomaly, metrics)
        logger.info(f"Anomaly written to blog: {blog_path}")
    except Exception as e:
        logger.warning(f"Failed to write anomaly to blog: {e}")
    
    # Then send notification
    try:
        # Try to import notification system (available in agent-runner)
        try:
            from common.notifications import (
                get_notification_manager,
                NotificationLevel,
            )
            notifier = get_notification_manager()
        except ImportError:
            # Not available in router, just log
            logger.warning(
                f"ANOMALY DETECTED: {anomaly.metric_name} = {anomaly.current_value} "
                f"(baseline: {anomaly.baseline_value}, deviation: {anomaly.deviation:.2f}σ, "
                f"severity: {anomaly.severity.value})"
            )
            return
        
        # Map anomaly severity to notification level
        severity_map = {
            "critical": NotificationLevel.CRITICAL,
            "warning": NotificationLevel.HIGH,
            "info": NotificationLevel.MEDIUM,
        }
        
        notification_level = severity_map.get(anomaly.severity.value, NotificationLevel.MEDIUM)
        
        # Create descriptive message
        deviation_pct = ((anomaly.current_value - anomaly.baseline_value) / anomaly.baseline_value * 100) if anomaly.baseline_value != 0 else 0
        
        title = f"Anomaly Detected: {anomaly.metric_name}"
        message = (
            f"Current value: {anomaly.current_value:.2f} "
            f"(baseline: {anomaly.baseline_value:.2f}, "
            f"deviation: {anomaly.deviation:.2f}σ, "
            f"{deviation_pct:+.1f}%)"
        )
        
        notifier.notify(
            level=notification_level,
            title=title,
            message=message,
            category="anomaly",
            source="anomaly_detector",
            metadata={
                "metric_name": anomaly.metric_name,
                "current_value": anomaly.current_value,
                "baseline_value": anomaly.baseline_value,
                "deviation": anomaly.deviation,
                "severity": anomaly.severity.value,
                "timestamp": anomaly.timestamp,
                **anomaly.metadata,
            }
        )
        
        logger.warning(
            f"Anomaly notification sent: {anomaly.metric_name} = {anomaly.current_value} "
            f"(deviation: {anomaly.deviation:.2f}σ, severity: {anomaly.severity.value})"
        )
        
    except Exception as e:
        logger.error(f"Failed to send anomaly notification: {e}", exc_info=True)

