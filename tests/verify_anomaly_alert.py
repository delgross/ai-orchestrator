import asyncio
import sys
import os
import random
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.observability import ObservabilitySystem, SystemMetrics, EfficiencyMetrics
from common.unified_tracking import get_unified_tracker, EventSeverity, EventCategory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_anomaly")

async def run_verification():
    logger.info("Starting Anomaly Detection Verification...")
    
    # Initialize systems
    obs_system = ObservabilitySystem(storage_path=Path("./temp_obs_data"))
    tracker = get_unified_tracker()
    
    # Mock the tracker.track_event to verify calls without sending real notifications
    original_track_event = tracker.track_event
    alert_triggered = False
    captured_events = []
    
    def mock_track_event(**kwargs):
        nonlocal alert_triggered
        if kwargs.get('category') == EventCategory.ANOMALY:
            logger.info(f"✅ ALERT TRIGGERED: {kwargs.get('message')}")
            alert_triggered = True
            captured_events.append(kwargs)
        # Call original to ensure no errors
        original_track_event(**kwargs)
        
    tracker.track_event = mock_track_event
    
    # 1. Establish Baseline (Normal Data)
    logger.info("Phase 1: Establishing Baseline (Latency ~100ms)...")
    base_metrics = SystemMetrics(
        timestamp=0,
        active_requests=10,
        completed_requests_1min=60,
        error_rate_1min=0.01,
        avg_response_time_1min=100.0,
        component_health={},
        efficiency=EfficiencyMetrics(requests_per_second=1.0)
    )
    
    # Feed 100 normal data points
    for i in range(100):
        # Add slight jitter
        jitter = random.uniform(-10, 10)
        metric = SystemMetrics(
            timestamp=i,
            active_requests=10,
            completed_requests_1min=60,
            error_rate_1min=0.01,
            avg_response_time_1min=100.0 + jitter,
            component_health={},
            efficiency=EfficiencyMetrics(requests_per_second=1.0)
        )
        obs_system._feed_metrics_to_detector(metric)
    
    logger.info("Baseline established.")
    
    # 2. Inject Anomaly (Latency Spike)
    logger.info("Phase 2: Injecting Anomaly (Latency 5000ms)...")
    anomaly_metric = SystemMetrics(
        timestamp=101,
        active_requests=10,
        completed_requests_1min=60,
        error_rate_1min=0.01,
        avg_response_time_1min=5000.0, # Huge spike
        component_health={},
        efficiency=EfficiencyMetrics(requests_per_second=1.0)
    )
    
    # Update system metrics (which feeds detector)
    obs_system.system_metrics_history.append(anomaly_metric)
    
    # Run user-facing detection which triggers the alert logic
    logger.info("Running detection...")
    anomalies = await obs_system.detect_anomalies()
    
    # 3. Verify Results
    if anomalies:
        logger.info(f"Detected {len(anomalies)} anomalies: {[a.metric_name for a in anomalies]}")
    else:
        logger.error("❌ No anomalies detected by detector!")
        
    if alert_triggered:
        logger.info("✅ SUCCESS: Alert was triggered and routed to Unified Tracker.")
        print("VERIFICATION_SUCCESS")
    else:
        logger.error("❌ FAILURE: Alert was NOT triggered.")
        print("VERIFICATION_FAILURE")

if __name__ == "__main__":
    asyncio.run(run_verification())
