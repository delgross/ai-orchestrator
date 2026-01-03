---
timestamp: 1767417648.204576
datetime: '2026-01-03T00:20:48.204576'
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
  anomaly_id: requests_per_second_1767417648.204576
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 34.46666666666667
    baseline_value: 35.25
    deviation: 1.5161290322580636
    severity: warning
    percentage_change: -2.2222222222222165
  system_state:
    active_requests: 27
    completed_requests_1min: 2068
    error_rate_1min: 0.0
    avg_response_time_1min: 894.5217108357575
  metadata: {}
  efficiency:
    requests_per_second: 34.46666666666667
    cache_hit_rate: 0.0
    queue_depth: 27
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 34.47
- **Baseline Value**: 35.25
- **Deviation**: 1.52 standard deviations
- **Change**: -2.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 27
- **Completed Requests (1min)**: 2068
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 894.52ms

### Efficiency Metrics

- **Requests/sec**: 34.47
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 27

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 34.46666666666667,
    "baseline_value": 35.25,
    "deviation": 1.5161290322580636,
    "severity": "warning",
    "percentage_change": -2.2222222222222165
  },
  "system_state": {
    "active_requests": 27,
    "completed_requests_1min": 2068,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 894.5217108357575
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 34.46666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 27
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
