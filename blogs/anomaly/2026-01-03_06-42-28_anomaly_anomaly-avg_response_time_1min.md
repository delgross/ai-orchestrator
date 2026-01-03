---
timestamp: 1767440548.15413
datetime: '2026-01-03T06:42:28.154130'
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
  anomaly_id: avg_response_time_1min_1767440548.15413
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 538.0843825200025
    baseline_value: 521.18074859398
    deviation: 2.4150686967405885
    severity: warning
    percentage_change: 3.2433342888478593
  system_state:
    active_requests: 7
    completed_requests_1min: 680
    error_rate_1min: 0.0
    avg_response_time_1min: 538.0843825200025
  metadata: {}
  efficiency:
    requests_per_second: 11.333333333333334
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 538.08
- **Baseline Value**: 521.18
- **Deviation**: 2.42 standard deviations
- **Change**: +3.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 680
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 538.08ms

### Efficiency Metrics

- **Requests/sec**: 11.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 538.0843825200025,
    "baseline_value": 521.18074859398,
    "deviation": 2.4150686967405885,
    "severity": "warning",
    "percentage_change": 3.2433342888478593
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 680,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 538.0843825200025
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
