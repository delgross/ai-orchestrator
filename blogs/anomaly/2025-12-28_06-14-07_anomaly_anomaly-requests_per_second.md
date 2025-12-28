---
timestamp: 1766920447.96987
datetime: '2025-12-28T06:14:07.969870'
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
  anomaly_id: requests_per_second_1766920447.96987
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.3166666666666667
    baseline_value: 0.93445
    deviation: 6.945755414666103
    severity: critical
    percentage_change: 40.902848377833664
  system_state:
    active_requests: 1
    completed_requests_1min: 79
    error_rate_1min: 0.0
    avg_response_time_1min: 441.34236891058424
  metadata: {}
  efficiency:
    requests_per_second: 1.3166666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.32
- **Baseline Value**: 0.93
- **Deviation**: 6.95 standard deviations
- **Change**: +40.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 79
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 441.34ms

### Efficiency Metrics

- **Requests/sec**: 1.32
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.3166666666666667,
    "baseline_value": 0.93445,
    "deviation": 6.945755414666103,
    "severity": "critical",
    "percentage_change": 40.902848377833664
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 79,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 441.34236891058424
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3166666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
