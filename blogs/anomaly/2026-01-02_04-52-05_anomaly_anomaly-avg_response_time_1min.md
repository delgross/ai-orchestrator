---
timestamp: 1767347525.7879739
datetime: '2026-01-02T04:52:05.787974'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767347525.7879739
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 438.5917108897863
    baseline_value: 432.6540435371718
    deviation: 2.051879901110214
    severity: warning
    percentage_change: 1.372382262759183
  system_state:
    active_requests: 6
    completed_requests_1min: 827
    error_rate_1min: 0.0
    avg_response_time_1min: 438.5917108897863
  metadata: {}
  efficiency:
    requests_per_second: 13.783333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 438.59
- **Baseline Value**: 432.65
- **Deviation**: 2.05 standard deviations
- **Change**: +1.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 827
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 438.59ms

### Efficiency Metrics

- **Requests/sec**: 13.78
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 438.5917108897863,
    "baseline_value": 432.6540435371718,
    "deviation": 2.051879901110214,
    "severity": "warning",
    "percentage_change": 1.372382262759183
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 827,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 438.5917108897863
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.783333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
