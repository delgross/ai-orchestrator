---
timestamp: 1767313924.6609879
datetime: '2026-01-01T19:32:04.660988'
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
  anomaly_id: requests_per_second_1767313924.6609879
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.416666666666667
    baseline_value: 2.9166666666666665
    deviation: 2.8767123287671237
    severity: warning
    percentage_change: 120.00000000000001
  system_state:
    active_requests: 1
    completed_requests_1min: 385
    error_rate_1min: 0.0
    avg_response_time_1min: 224.25438521744368
  metadata: {}
  efficiency:
    requests_per_second: 6.416666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.42
- **Baseline Value**: 2.92
- **Deviation**: 2.88 standard deviations
- **Change**: +120.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 385
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 224.25ms

### Efficiency Metrics

- **Requests/sec**: 6.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.416666666666667,
    "baseline_value": 2.9166666666666665,
    "deviation": 2.8767123287671237,
    "severity": "warning",
    "percentage_change": 120.00000000000001
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 385,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 224.25438521744368
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.416666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
