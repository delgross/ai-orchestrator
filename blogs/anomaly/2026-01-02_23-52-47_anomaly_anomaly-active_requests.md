---
timestamp: 1767415967.288585
datetime: '2026-01-02T23:52:47.288585'
category: anomaly
severity: warning
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: active_requests_1767415967.288585
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 33.0
    baseline_value: 10.0
    deviation: 2.3
    severity: warning
    percentage_change: 229.99999999999997
  system_state:
    active_requests: 33
    completed_requests_1min: 932
    error_rate_1min: 0.0
    avg_response_time_1min: 1994.3235490966765
  metadata: {}
  efficiency:
    requests_per_second: 15.533333333333333
    cache_hit_rate: 0.0
    queue_depth: 33
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 33.00
- **Baseline Value**: 10.00
- **Deviation**: 2.30 standard deviations
- **Change**: +230.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 33
- **Completed Requests (1min)**: 932
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1994.32ms

### Efficiency Metrics

- **Requests/sec**: 15.53
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 33

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 33.0,
    "baseline_value": 10.0,
    "deviation": 2.3,
    "severity": "warning",
    "percentage_change": 229.99999999999997
  },
  "system_state": {
    "active_requests": 33,
    "completed_requests_1min": 932,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1994.3235490966765
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 15.533333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 33
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
