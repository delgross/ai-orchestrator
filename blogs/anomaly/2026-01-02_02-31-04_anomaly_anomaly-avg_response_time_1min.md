---
timestamp: 1767339064.573042
datetime: '2026-01-02T02:31:04.573042'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767339064.573042
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 440.9039136135217
    baseline_value: 433.20008369964125
    deviation: 1.8672591298411578
    severity: warning
    percentage_change: 1.778353745476624
  system_state:
    active_requests: 6
    completed_requests_1min: 825
    error_rate_1min: 0.0
    avg_response_time_1min: 440.9039136135217
  metadata: {}
  efficiency:
    requests_per_second: 13.75
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 440.90
- **Baseline Value**: 433.20
- **Deviation**: 1.87 standard deviations
- **Change**: +1.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 825
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 440.90ms

### Efficiency Metrics

- **Requests/sec**: 13.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 440.9039136135217,
    "baseline_value": 433.20008369964125,
    "deviation": 1.8672591298411578,
    "severity": "warning",
    "percentage_change": 1.778353745476624
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 825,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 440.9039136135217
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
