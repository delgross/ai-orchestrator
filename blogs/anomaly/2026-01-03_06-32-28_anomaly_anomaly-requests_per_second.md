---
timestamp: 1767439948.023791
datetime: '2026-01-03T06:32:28.023791'
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
  anomaly_id: requests_per_second_1767439948.023791
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.683333333333334
    baseline_value: 11.466666666666667
    deviation: 1.6250000000000067
    severity: warning
    percentage_change: 1.8895348837209311
  system_state:
    active_requests: 6
    completed_requests_1min: 701
    error_rate_1min: 0.0
    avg_response_time_1min: 541.0548555697932
  metadata: {}
  efficiency:
    requests_per_second: 11.683333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.68
- **Baseline Value**: 11.47
- **Deviation**: 1.63 standard deviations
- **Change**: +1.9%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 701
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 541.05ms

### Efficiency Metrics

- **Requests/sec**: 11.68
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.683333333333334,
    "baseline_value": 11.466666666666667,
    "deviation": 1.6250000000000067,
    "severity": "warning",
    "percentage_change": 1.8895348837209311
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 701,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 541.0548555697932
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.683333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
