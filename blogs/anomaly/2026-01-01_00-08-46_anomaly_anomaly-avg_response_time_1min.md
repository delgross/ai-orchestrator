---
timestamp: 1767244126.2834718
datetime: '2026-01-01T00:08:46.283472'
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
  anomaly_id: avg_response_time_1min_1767244126.2834718
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 0.0
    baseline_value: 161.96704679919827
    deviation: 8.405426375772011
    severity: critical
    percentage_change: -100.0
  system_state:
    active_requests: 0
    completed_requests_1min: 0
    error_rate_1min: 0.0
    avg_response_time_1min: 0.0
  metadata: {}
  efficiency:
    requests_per_second: 0.0
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 0.00
- **Baseline Value**: 161.97
- **Deviation**: 8.41 standard deviations
- **Change**: -100.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 0
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 0.00ms

### Efficiency Metrics

- **Requests/sec**: 0.00
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
    "current_value": 0.0,
    "baseline_value": 161.96704679919827,
    "deviation": 8.405426375772011,
    "severity": "critical",
    "percentage_change": -100.0
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 0,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 0.0
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.0,
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
