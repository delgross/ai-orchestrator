---
timestamp: 1767431126.169055
datetime: '2026-01-03T04:05:26.169055'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1767431126.169055
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.183333333333334
    baseline_value: 11.383333333333333
    deviation: 2.0
    severity: warning
    percentage_change: -1.7569546120058503
  system_state:
    active_requests: 6
    completed_requests_1min: 671
    error_rate_1min: 0.0
    avg_response_time_1min: 535.8229298172338
  metadata: {}
  efficiency:
    requests_per_second: 11.183333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.18
- **Baseline Value**: 11.38
- **Deviation**: 2.00 standard deviations
- **Change**: -1.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 671
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 535.82ms

### Efficiency Metrics

- **Requests/sec**: 11.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.183333333333334,
    "baseline_value": 11.383333333333333,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": -1.7569546120058503
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 671,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 535.8229298172338
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.183333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
