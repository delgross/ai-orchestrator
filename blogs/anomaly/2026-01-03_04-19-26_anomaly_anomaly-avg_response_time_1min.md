---
timestamp: 1767431966.356582
datetime: '2026-01-03T04:19:26.356582'
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
  anomaly_id: avg_response_time_1min_1767431966.356582
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 523.5416990127006
    baseline_value: 538.568451530055
    deviation: 2.108132145771239
    severity: warning
    percentage_change: -2.7901286223995925
  system_state:
    active_requests: 6
    completed_requests_1min: 685
    error_rate_1min: 0.0
    avg_response_time_1min: 523.5416990127006
  metadata: {}
  efficiency:
    requests_per_second: 11.416666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 523.54
- **Baseline Value**: 538.57
- **Deviation**: 2.11 standard deviations
- **Change**: -2.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 685
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 523.54ms

### Efficiency Metrics

- **Requests/sec**: 11.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 523.5416990127006,
    "baseline_value": 538.568451530055,
    "deviation": 2.108132145771239,
    "severity": "warning",
    "percentage_change": -2.7901286223995925
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 685,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 523.5416990127006
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.416666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
