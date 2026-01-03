---
timestamp: 1767395690.688805
datetime: '2026-01-02T18:14:50.688805'
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
  anomaly_id: requests_per_second_1767395690.688805
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.066666666666666
    baseline_value: 12.516666666666667
    deviation: 2.906249999999989
    severity: warning
    percentage_change: 12.383488681757647
  system_state:
    active_requests: 7
    completed_requests_1min: 844
    error_rate_1min: 0.0
    avg_response_time_1min: 465.38973956311486
  metadata: {}
  efficiency:
    requests_per_second: 14.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.07
- **Baseline Value**: 12.52
- **Deviation**: 2.91 standard deviations
- **Change**: +12.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 844
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 465.39ms

### Efficiency Metrics

- **Requests/sec**: 14.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.066666666666666,
    "baseline_value": 12.516666666666667,
    "deviation": 2.906249999999989,
    "severity": "warning",
    "percentage_change": 12.383488681757647
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 844,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 465.38973956311486
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.066666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
