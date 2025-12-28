---
timestamp: 1766865604.170248
datetime: '2025-12-27T15:00:04.170248'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1766865604.170248
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5.176967045046249
    baseline_value: 125.90953502099778
    deviation: 8.71768121823666
    severity: critical
    percentage_change: -95.88834392551533
  system_state:
    active_requests: 0
    completed_requests_1min: 53
    error_rate_1min: 0.0
    avg_response_time_1min: 5.176967045046249
  metadata: {}
  efficiency:
    requests_per_second: 0.8833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5.18
- **Baseline Value**: 125.91
- **Deviation**: 8.72 standard deviations
- **Change**: -95.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 53
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 5.18ms

### Efficiency Metrics

- **Requests/sec**: 0.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 5.176967045046249,
    "baseline_value": 125.90953502099778,
    "deviation": 8.71768121823666,
    "severity": "critical",
    "percentage_change": -95.88834392551533
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 53,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 5.176967045046249
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
