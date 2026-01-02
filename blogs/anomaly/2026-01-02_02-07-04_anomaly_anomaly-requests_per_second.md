---
timestamp: 1767337624.416259
datetime: '2026-01-02T02:07:04.416259'
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
  anomaly_id: requests_per_second_1767337624.416259
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.15
    baseline_value: 13.95
    deviation: 2.0000000000000178
    severity: warning
    percentage_change: 1.433691756272409
  system_state:
    active_requests: 6
    completed_requests_1min: 849
    error_rate_1min: 0.0
    avg_response_time_1min: 438.8141957834556
  metadata: {}
  efficiency:
    requests_per_second: 14.15
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.15
- **Baseline Value**: 13.95
- **Deviation**: 2.00 standard deviations
- **Change**: +1.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 849
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 438.81ms

### Efficiency Metrics

- **Requests/sec**: 14.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.15,
    "baseline_value": 13.95,
    "deviation": 2.0000000000000178,
    "severity": "warning",
    "percentage_change": 1.433691756272409
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 849,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 438.8141957834556
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
