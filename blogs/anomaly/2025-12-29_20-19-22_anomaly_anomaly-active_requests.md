---
timestamp: 1767057562.729644
datetime: '2025-12-29T20:19:22.729644'
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
  anomaly_id: active_requests_1767057562.729644
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 8.0
    baseline_value: 0.684
    deviation: 5.036238683899808
    severity: warning
    percentage_change: 1069.5906432748536
  system_state:
    active_requests: 8
    completed_requests_1min: 70
    error_rate_1min: 0.0
    avg_response_time_1min: 6985.971508707319
  metadata: {}
  efficiency:
    requests_per_second: 1.1666666666666667
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 8.00
- **Baseline Value**: 0.68
- **Deviation**: 5.04 standard deviations
- **Change**: +1069.6%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 70
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 6985.97ms

### Efficiency Metrics

- **Requests/sec**: 1.17
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 8.0,
    "baseline_value": 0.684,
    "deviation": 5.036238683899808,
    "severity": "warning",
    "percentage_change": 1069.5906432748536
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 70,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 6985.971508707319
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
