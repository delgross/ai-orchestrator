---
timestamp: 1767055522.591155
datetime: '2025-12-29T19:45:22.591155'
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
  anomaly_id: requests_per_second_1767055522.591155
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 4.616666666666666
    baseline_value: 0.6115666666666667
    deviation: 5.380492120321874
    severity: warning
    percentage_change: 654.8918079250012
  system_state:
    active_requests: 2
    completed_requests_1min: 277
    error_rate_1min: 0.0
    avg_response_time_1min: 1370.41681337873
  metadata: {}
  efficiency:
    requests_per_second: 4.616666666666666
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 4.62
- **Baseline Value**: 0.61
- **Deviation**: 5.38 standard deviations
- **Change**: +654.9%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 277
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1370.42ms

### Efficiency Metrics

- **Requests/sec**: 4.62
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 4.616666666666666,
    "baseline_value": 0.6115666666666667,
    "deviation": 5.380492120321874,
    "severity": "warning",
    "percentage_change": 654.8918079250012
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 277,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1370.41681337873
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.616666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
