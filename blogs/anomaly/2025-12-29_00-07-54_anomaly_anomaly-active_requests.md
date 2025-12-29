---
timestamp: 1766984874.5212119
datetime: '2025-12-29T00:07:54.521212'
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
  anomaly_id: active_requests_1766984874.5212119
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 2.0
    baseline_value: 0.98
    deviation: 4.042540299795625
    severity: warning
    percentage_change: 104.08163265306123
  system_state:
    active_requests: 2
    completed_requests_1min: 94
    error_rate_1min: 0.0
    avg_response_time_1min: 158.63406150899036
  metadata: {}
  efficiency:
    requests_per_second: 1.5666666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 2.00
- **Baseline Value**: 0.98
- **Deviation**: 4.04 standard deviations
- **Change**: +104.1%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 94
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 158.63ms

### Efficiency Metrics

- **Requests/sec**: 1.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 2.0,
    "baseline_value": 0.98,
    "deviation": 4.042540299795625,
    "severity": "warning",
    "percentage_change": 104.08163265306123
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 94,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 158.63406150899036
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
