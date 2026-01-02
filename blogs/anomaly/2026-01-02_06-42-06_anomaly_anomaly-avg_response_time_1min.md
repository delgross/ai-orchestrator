---
timestamp: 1767354126.878686
datetime: '2026-01-02T06:42:06.878686'
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
  anomaly_id: avg_response_time_1min_1767354126.878686
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 513.0202817561905
    baseline_value: 469.8151916849847
    deviation: 2.1387895359981597
    severity: warning
    percentage_change: 9.196188381276343
  system_state:
    active_requests: 7
    completed_requests_1min: 806
    error_rate_1min: 0.0
    avg_response_time_1min: 513.0202817561905
  metadata: {}
  efficiency:
    requests_per_second: 13.433333333333334
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 513.02
- **Baseline Value**: 469.82
- **Deviation**: 2.14 standard deviations
- **Change**: +9.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 806
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 513.02ms

### Efficiency Metrics

- **Requests/sec**: 13.43
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 513.0202817561905,
    "baseline_value": 469.8151916849847,
    "deviation": 2.1387895359981597,
    "severity": "warning",
    "percentage_change": 9.196188381276343
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 806,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 513.0202817561905
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.433333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
