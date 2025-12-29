---
timestamp: 1766985054.535687
datetime: '2025-12-29T00:10:54.535687'
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
  anomaly_id: avg_response_time_1min_1766985054.535687
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 216.91478028589364
    baseline_value: 152.32493903706938
    deviation: 4.3646764646594445
    severity: warning
    percentage_change: 42.402670013940295
  system_state:
    active_requests: 0
    completed_requests_1min: 98
    error_rate_1min: 0.0
    avg_response_time_1min: 216.91478028589364
  metadata: {}
  efficiency:
    requests_per_second: 1.6333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 216.91
- **Baseline Value**: 152.32
- **Deviation**: 4.36 standard deviations
- **Change**: +42.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 98
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 216.91ms

### Efficiency Metrics

- **Requests/sec**: 1.63
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 216.91478028589364,
    "baseline_value": 152.32493903706938,
    "deviation": 4.3646764646594445,
    "severity": "warning",
    "percentage_change": 42.402670013940295
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 98,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 216.91478028589364
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
