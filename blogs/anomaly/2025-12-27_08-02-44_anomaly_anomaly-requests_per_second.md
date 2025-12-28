---
timestamp: 1766840564.6685271
datetime: '2025-12-27T08:02:44.668527'
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
  anomaly_id: requests_per_second_1766840564.6685271
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.35
    baseline_value: 0.144281045751634
    deviation: 4.647067903907693
    severity: warning
    percentage_change: 835.6738391845979
  system_state:
    active_requests: 0
    completed_requests_1min: 81
    error_rate_1min: 0.0
    avg_response_time_1min: 19.143151648250626
  metadata: {}
  efficiency:
    requests_per_second: 1.35
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.35
- **Baseline Value**: 0.14
- **Deviation**: 4.65 standard deviations
- **Change**: +835.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 81
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 19.14ms

### Efficiency Metrics

- **Requests/sec**: 1.35
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.35,
    "baseline_value": 0.144281045751634,
    "deviation": 4.647067903907693,
    "severity": "warning",
    "percentage_change": 835.6738391845979
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 81,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 19.143151648250626
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.35,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
