---
timestamp: 1767429025.6888509
datetime: '2026-01-03T03:30:25.688851'
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
  anomaly_id: requests_per_second_1767429025.6888509
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.133333333333333
    baseline_value: 11.316666666666666
    deviation: 1.5714285714285672
    severity: warning
    percentage_change: -1.6200294550810037
  system_state:
    active_requests: 6
    completed_requests_1min: 668
    error_rate_1min: 0.0
    avg_response_time_1min: 540.0253412966243
  metadata: {}
  efficiency:
    requests_per_second: 11.133333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.13
- **Baseline Value**: 11.32
- **Deviation**: 1.57 standard deviations
- **Change**: -1.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 668
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 540.03ms

### Efficiency Metrics

- **Requests/sec**: 11.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.133333333333333,
    "baseline_value": 11.316666666666666,
    "deviation": 1.5714285714285672,
    "severity": "warning",
    "percentage_change": -1.6200294550810037
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 668,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 540.0253412966243
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.133333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
