---
timestamp: 1767458254.5389068
datetime: '2026-01-03T11:37:34.538907'
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
  anomaly_id: avg_response_time_1min_1767458254.5389068
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 0.0
    baseline_value: 335.39497195266364
    deviation: 1.9207983177284096
    severity: warning
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
- **Baseline Value**: 335.39
- **Deviation**: 1.92 standard deviations
- **Change**: -100.0%
- **Severity**: WARNING

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



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 0.0,
    "baseline_value": 335.39497195266364,
    "deviation": 1.9207983177284096,
    "severity": "warning",
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
