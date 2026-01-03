---
timestamp: 1767415667.13817
datetime: '2026-01-02T23:47:47.138170'
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
  anomaly_id: active_requests_1767415667.13817
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 29.0
    baseline_value: 10.0
    deviation: 1.9
    severity: warning
    percentage_change: 190.0
  system_state:
    active_requests: 29
    completed_requests_1min: 709
    error_rate_1min: 0.0
    avg_response_time_1min: 3012.196311157076
  metadata: {}
  efficiency:
    requests_per_second: 11.816666666666666
    cache_hit_rate: 0.0
    queue_depth: 29
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 29.00
- **Baseline Value**: 10.00
- **Deviation**: 1.90 standard deviations
- **Change**: +190.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 29
- **Completed Requests (1min)**: 709
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3012.20ms

### Efficiency Metrics

- **Requests/sec**: 11.82
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 29

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 29.0,
    "baseline_value": 10.0,
    "deviation": 1.9,
    "severity": "warning",
    "percentage_change": 190.0
  },
  "system_state": {
    "active_requests": 29,
    "completed_requests_1min": 709,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3012.196311157076
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.816666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 29
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
