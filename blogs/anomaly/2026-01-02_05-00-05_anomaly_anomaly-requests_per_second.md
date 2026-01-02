---
timestamp: 1767348005.8731241
datetime: '2026-01-02T05:00:05.873124'
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
  anomaly_id: requests_per_second_1767348005.8731241
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.966666666666667
    baseline_value: 13.833333333333334
    deviation: 1.599999999999983
    severity: warning
    percentage_change: 0.9638554216867437
  system_state:
    active_requests: 6
    completed_requests_1min: 838
    error_rate_1min: 0.0
    avg_response_time_1min: 432.10516027163777
  metadata: {}
  efficiency:
    requests_per_second: 13.966666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.97
- **Baseline Value**: 13.83
- **Deviation**: 1.60 standard deviations
- **Change**: +1.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 838
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 432.11ms

### Efficiency Metrics

- **Requests/sec**: 13.97
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.966666666666667,
    "baseline_value": 13.833333333333334,
    "deviation": 1.599999999999983,
    "severity": "warning",
    "percentage_change": 0.9638554216867437
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 838,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 432.10516027163777
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.966666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
