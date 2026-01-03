---
timestamp: 1767442828.776834
datetime: '2026-01-03T07:20:28.776834'
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
  anomaly_id: requests_per_second_1767442828.776834
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 10.766666666666667
    baseline_value: 11.016666666666667
    deviation: 1.8750000000000067
    severity: warning
    percentage_change: -2.26928895612708
  system_state:
    active_requests: 6
    completed_requests_1min: 646
    error_rate_1min: 0.0
    avg_response_time_1min: 556.0987877771951
  metadata: {}
  efficiency:
    requests_per_second: 10.766666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 10.77
- **Baseline Value**: 11.02
- **Deviation**: 1.88 standard deviations
- **Change**: -2.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 646
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 556.10ms

### Efficiency Metrics

- **Requests/sec**: 10.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 10.766666666666667,
    "baseline_value": 11.016666666666667,
    "deviation": 1.8750000000000067,
    "severity": "warning",
    "percentage_change": -2.26928895612708
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 646,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 556.0987877771951
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.766666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
