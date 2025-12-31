---
timestamp: 1767192855.638421
datetime: '2025-12-31T09:54:15.638421'
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
  anomaly_id: avg_response_time_1min_1767192855.638421
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 207.03113079071045
    baseline_value: 104.20607216656208
    deviation: 9.65384303297366
    severity: critical
    percentage_change: 98.67472834000853
  system_state:
    active_requests: 0
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 207.03113079071045
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 207.03
- **Baseline Value**: 104.21
- **Deviation**: 9.65 standard deviations
- **Change**: +98.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 207.03ms

### Efficiency Metrics

- **Requests/sec**: 0.10
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
    "current_value": 207.03113079071045,
    "baseline_value": 104.20607216656208,
    "deviation": 9.65384303297366,
    "severity": "critical",
    "percentage_change": 98.67472834000853
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 207.03113079071045
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
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
