---
timestamp: 1767439047.819011
datetime: '2026-01-03T06:17:27.819011'
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
  anomaly_id: requests_per_second_1767439047.819011
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.616666666666667
    baseline_value: 11.366666666666667
    deviation: 2.1428571428571344
    severity: warning
    percentage_change: 2.19941348973607
  system_state:
    active_requests: 6
    completed_requests_1min: 697
    error_rate_1min: 0.0
    avg_response_time_1min: 523.8718476835933
  metadata: {}
  efficiency:
    requests_per_second: 11.616666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.62
- **Baseline Value**: 11.37
- **Deviation**: 2.14 standard deviations
- **Change**: +2.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 697
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 523.87ms

### Efficiency Metrics

- **Requests/sec**: 11.62
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.616666666666667,
    "baseline_value": 11.366666666666667,
    "deviation": 2.1428571428571344,
    "severity": "warning",
    "percentage_change": 2.19941348973607
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 697,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 523.8718476835933
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.616666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
