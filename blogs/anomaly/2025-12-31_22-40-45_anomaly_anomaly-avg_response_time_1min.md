---
timestamp: 1767238845.728406
datetime: '2025-12-31T22:40:45.728406'
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
  anomaly_id: avg_response_time_1min_1767238845.728406
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 199.9268570253926
    baseline_value: 180.14507139882733
    deviation: 1.5938476172181244
    severity: warning
    percentage_change: 10.981030717609762
  system_state:
    active_requests: 0
    completed_requests_1min: 62
    error_rate_1min: 0.0
    avg_response_time_1min: 199.9268570253926
  metadata: {}
  efficiency:
    requests_per_second: 1.0333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 199.93
- **Baseline Value**: 180.15
- **Deviation**: 1.59 standard deviations
- **Change**: +11.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 62
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 199.93ms

### Efficiency Metrics

- **Requests/sec**: 1.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 199.9268570253926,
    "baseline_value": 180.14507139882733,
    "deviation": 1.5938476172181244,
    "severity": "warning",
    "percentage_change": 10.981030717609762
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 62,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 199.9268570253926
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
