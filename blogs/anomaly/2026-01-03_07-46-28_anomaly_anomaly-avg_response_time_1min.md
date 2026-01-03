---
timestamp: 1767444388.979486
datetime: '2026-01-03T07:46:28.979486'
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
  anomaly_id: avg_response_time_1min_1767444388.979486
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 379.95076481300066
    baseline_value: 549.8170652830532
    deviation: 5.734412811902663
    severity: critical
    percentage_change: -30.895057864856035
  system_state:
    active_requests: 1
    completed_requests_1min: 158
    error_rate_1min: 0.0
    avg_response_time_1min: 379.95076481300066
  metadata: {}
  efficiency:
    requests_per_second: 2.6333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 379.95
- **Baseline Value**: 549.82
- **Deviation**: 5.73 standard deviations
- **Change**: -30.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 158
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 379.95ms

### Efficiency Metrics

- **Requests/sec**: 2.63
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 379.95076481300066,
    "baseline_value": 549.8170652830532,
    "deviation": 5.734412811902663,
    "severity": "critical",
    "percentage_change": -30.895057864856035
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 158,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 379.95076481300066
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.6333333333333333,
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
