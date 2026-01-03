---
timestamp: 1767419268.892527
datetime: '2026-01-03T00:47:48.892527'
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
  anomaly_id: avg_response_time_1min_1767419268.892527
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 746.7817673721466
    baseline_value: 885.6795525705583
    deviation: 2.647180392254129
    severity: warning
    percentage_change: -15.682622997819093
  system_state:
    active_requests: 27
    completed_requests_1min: 1992
    error_rate_1min: 0.0
    avg_response_time_1min: 746.7817673721466
  metadata: {}
  efficiency:
    requests_per_second: 33.2
    cache_hit_rate: 0.0
    queue_depth: 27
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 746.78
- **Baseline Value**: 885.68
- **Deviation**: 2.65 standard deviations
- **Change**: -15.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 27
- **Completed Requests (1min)**: 1992
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 746.78ms

### Efficiency Metrics

- **Requests/sec**: 33.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 27

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 746.7817673721466,
    "baseline_value": 885.6795525705583,
    "deviation": 2.647180392254129,
    "severity": "warning",
    "percentage_change": -15.682622997819093
  },
  "system_state": {
    "active_requests": 27,
    "completed_requests_1min": 1992,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 746.7817673721466
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 33.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 27
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
