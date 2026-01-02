---
timestamp: 1767340864.8246558
datetime: '2026-01-02T03:01:04.824656'
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
  anomaly_id: requests_per_second_1767340864.8246558
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.933333333333334
    baseline_value: 13.85
    deviation: 1.666666666666714
    severity: warning
    percentage_change: 0.6016847172081872
  system_state:
    active_requests: 6
    completed_requests_1min: 836
    error_rate_1min: 0.0
    avg_response_time_1min: 434.8621442557522
  metadata: {}
  efficiency:
    requests_per_second: 13.933333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.93
- **Baseline Value**: 13.85
- **Deviation**: 1.67 standard deviations
- **Change**: +0.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 836
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 434.86ms

### Efficiency Metrics

- **Requests/sec**: 13.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.933333333333334,
    "baseline_value": 13.85,
    "deviation": 1.666666666666714,
    "severity": "warning",
    "percentage_change": 0.6016847172081872
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 836,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 434.8621442557522
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.933333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
