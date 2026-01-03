---
timestamp: 1767414826.590668
datetime: '2026-01-02T23:33:46.590668'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767414826.590668
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.9
    baseline_value: 0.1
    deviation: 153.6
    severity: critical
    percentage_change: 12800.0
  system_state:
    active_requests: 20
    completed_requests_1min: 774
    error_rate_1min: 0.0
    avg_response_time_1min: 1616.0569499013343
  metadata: {}
  efficiency:
    requests_per_second: 12.9
    cache_hit_rate: 0.0
    queue_depth: 20
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.90
- **Baseline Value**: 0.10
- **Deviation**: 153.60 standard deviations
- **Change**: +12800.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 20
- **Completed Requests (1min)**: 774
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1616.06ms

### Efficiency Metrics

- **Requests/sec**: 12.90
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 20

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.9,
    "baseline_value": 0.1,
    "deviation": 153.6,
    "severity": "critical",
    "percentage_change": 12800.0
  },
  "system_state": {
    "active_requests": 20,
    "completed_requests_1min": 774,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1616.0569499013343
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.9,
    "cache_hit_rate": 0.0,
    "queue_depth": 20
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
