---
timestamp: 1766979234.089097
datetime: '2025-12-28T22:33:54.089097'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1766979234.089097
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 3.15
    baseline_value: 1.5977752639517346
    deviation: 4.341888208809233
    severity: warning
    percentage_change: 97.14912798244163
  system_state:
    active_requests: 1
    completed_requests_1min: 189
    error_rate_1min: 0.0
    avg_response_time_1min: 150.82413935787463
  metadata: {}
  efficiency:
    requests_per_second: 3.15
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 3.15
- **Baseline Value**: 1.60
- **Deviation**: 4.34 standard deviations
- **Change**: +97.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 189
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 150.82ms

### Efficiency Metrics

- **Requests/sec**: 3.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 3.15,
    "baseline_value": 1.5977752639517346,
    "deviation": 4.341888208809233,
    "severity": "warning",
    "percentage_change": 97.14912798244163
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 189,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 150.82413935787463
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
