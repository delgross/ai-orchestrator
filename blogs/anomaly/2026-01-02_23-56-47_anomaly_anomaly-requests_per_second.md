---
timestamp: 1767416207.4443672
datetime: '2026-01-02T23:56:47.444367'
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
  anomaly_id: requests_per_second_1767416207.4443672
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 27.616666666666667
    baseline_value: 9.25
    deviation: 1.9927667269439422
    severity: warning
    percentage_change: 198.55855855855856
  system_state:
    active_requests: 24
    completed_requests_1min: 1657
    error_rate_1min: 0.0
    avg_response_time_1min: 1591.004245455321
  metadata: {}
  efficiency:
    requests_per_second: 27.616666666666667
    cache_hit_rate: 0.0
    queue_depth: 24
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 27.62
- **Baseline Value**: 9.25
- **Deviation**: 1.99 standard deviations
- **Change**: +198.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 24
- **Completed Requests (1min)**: 1657
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1591.00ms

### Efficiency Metrics

- **Requests/sec**: 27.62
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 24

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 27.616666666666667,
    "baseline_value": 9.25,
    "deviation": 1.9927667269439422,
    "severity": "warning",
    "percentage_change": 198.55855855855856
  },
  "system_state": {
    "active_requests": 24,
    "completed_requests_1min": 1657,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1591.004245455321
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 27.616666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 24
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
