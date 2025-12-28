---
timestamp: 1766860743.823939
datetime: '2025-12-27T13:39:03.823939'
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
  anomaly_id: active_requests_1766860743.823939
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 3.0
    baseline_value: 1.013
    deviation: 4.063827479540725
    severity: warning
    percentage_change: 196.1500493583416
  system_state:
    active_requests: 3
    completed_requests_1min: 145
    error_rate_1min: 0.0
    avg_response_time_1min: 118.27280768032732
  metadata: {}
  efficiency:
    requests_per_second: 2.4166666666666665
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 3.00
- **Baseline Value**: 1.01
- **Deviation**: 4.06 standard deviations
- **Change**: +196.2%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 145
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 118.27ms

### Efficiency Metrics

- **Requests/sec**: 2.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 3.0,
    "baseline_value": 1.013,
    "deviation": 4.063827479540725,
    "severity": "warning",
    "percentage_change": 196.1500493583416
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 145,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 118.27280768032732
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.4166666666666665,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
