---
timestamp: 1767041961.7334359
datetime: '2025-12-29T15:59:21.733436'
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
  anomaly_id: active_requests_1767041961.7334359
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 6.0
    baseline_value: 0.2703583061889251
    deviation: 5.312222221162312
    severity: warning
    percentage_change: 2119.2771084337346
  system_state:
    active_requests: 6
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 72530.58562278748
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 6.00
- **Baseline Value**: 0.27
- **Deviation**: 5.31 standard deviations
- **Change**: +2119.3%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 72530.59ms

### Efficiency Metrics

- **Requests/sec**: 0.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 6.0,
    "baseline_value": 0.2703583061889251,
    "deviation": 5.312222221162312,
    "severity": "warning",
    "percentage_change": 2119.2771084337346
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 72530.58562278748
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
