---
timestamp: 1767422689.853477
datetime: '2026-01-03T01:44:49.853477'
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
  anomaly_id: avg_response_time_1min_1767422689.853477
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 454.06945575158664
    baseline_value: 496.6762077107149
    deviation: 1.513501172130488
    severity: warning
    percentage_change: -8.57837587097472
  system_state:
    active_requests: 6
    completed_requests_1min: 831
    error_rate_1min: 0.0
    avg_response_time_1min: 454.06945575158664
  metadata: {}
  efficiency:
    requests_per_second: 13.85
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 454.07
- **Baseline Value**: 496.68
- **Deviation**: 1.51 standard deviations
- **Change**: -8.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 831
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 454.07ms

### Efficiency Metrics

- **Requests/sec**: 13.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 454.06945575158664,
    "baseline_value": 496.6762077107149,
    "deviation": 1.513501172130488,
    "severity": "warning",
    "percentage_change": -8.57837587097472
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 831,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 454.06945575158664
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
