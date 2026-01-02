---
timestamp: 1767334864.0380008
datetime: '2026-01-02T01:21:04.038001'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767334864.0380008
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2141.035318374634
    baseline_value: 1084.476661682129
    deviation: 3.940131542563908
    severity: critical
    percentage_change: 97.425670281708
  system_state:
    active_requests: 0
    completed_requests_1min: 11
    error_rate_1min: 0.0
    avg_response_time_1min: 2141.035318374634
  metadata: {}
  efficiency:
    requests_per_second: 0.18333333333333332
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2141.04
- **Baseline Value**: 1084.48
- **Deviation**: 3.94 standard deviations
- **Change**: +97.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 11
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2141.04ms

### Efficiency Metrics

- **Requests/sec**: 0.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 2141.035318374634,
    "baseline_value": 1084.476661682129,
    "deviation": 3.940131542563908,
    "severity": "critical",
    "percentage_change": 97.425670281708
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 11,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2141.035318374634
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.18333333333333332,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
