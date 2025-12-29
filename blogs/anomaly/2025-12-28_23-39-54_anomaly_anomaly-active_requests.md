---
timestamp: 1766983194.376641
datetime: '2025-12-28T23:39:54.376641'
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
  anomaly_id: active_requests_1766983194.376641
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 0.0
    baseline_value: 1.005
    deviation: 4.962372080840011
    severity: warning
    percentage_change: -100.0
  system_state:
    active_requests: 0
    completed_requests_1min: 94
    error_rate_1min: 0.0
    avg_response_time_1min: 169.3874978004618
  metadata: {}
  efficiency:
    requests_per_second: 1.5666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 0.00
- **Baseline Value**: 1.00
- **Deviation**: 4.96 standard deviations
- **Change**: -100.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 94
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 169.39ms

### Efficiency Metrics

- **Requests/sec**: 1.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 0.0,
    "baseline_value": 1.005,
    "deviation": 4.962372080840011,
    "severity": "warning",
    "percentage_change": -100.0
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 94,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 169.3874978004618
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
