---
timestamp: 1767438207.623307
datetime: '2026-01-03T06:03:27.623307'
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
  anomaly_id: requests_per_second_1767438207.623307
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.833333333333334
    baseline_value: 11.583333333333334
    deviation: 2.9999999999999787
    severity: warning
    percentage_change: 2.158273381294964
  system_state:
    active_requests: 6
    completed_requests_1min: 710
    error_rate_1min: 0.0
    avg_response_time_1min: 513.444598627762
  metadata: {}
  efficiency:
    requests_per_second: 11.833333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.83
- **Baseline Value**: 11.58
- **Deviation**: 3.00 standard deviations
- **Change**: +2.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 710
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 513.44ms

### Efficiency Metrics

- **Requests/sec**: 11.83
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.833333333333334,
    "baseline_value": 11.583333333333334,
    "deviation": 2.9999999999999787,
    "severity": "warning",
    "percentage_change": 2.158273381294964
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 710,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 513.444598627762
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
