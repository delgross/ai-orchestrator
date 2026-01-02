---
timestamp: 1767315472.340725
datetime: '2026-01-01T19:57:52.340725'
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
  anomaly_id: requests_per_second_1767315472.340725
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.066666666666666
    baseline_value: 2.8833333333333333
    deviation: 1.7945205479452055
    severity: warning
    percentage_change: 75.72254335260115
  system_state:
    active_requests: 1
    completed_requests_1min: 304
    error_rate_1min: 0.0
    avg_response_time_1min: 269.8696781145899
  metadata: {}
  efficiency:
    requests_per_second: 5.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.07
- **Baseline Value**: 2.88
- **Deviation**: 1.79 standard deviations
- **Change**: +75.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 304
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 269.87ms

### Efficiency Metrics

- **Requests/sec**: 5.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.066666666666666,
    "baseline_value": 2.8833333333333333,
    "deviation": 1.7945205479452055,
    "severity": "warning",
    "percentage_change": 75.72254335260115
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 304,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 269.8696781145899
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.066666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
