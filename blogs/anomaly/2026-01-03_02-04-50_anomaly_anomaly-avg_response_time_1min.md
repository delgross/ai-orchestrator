---
timestamp: 1767423890.220711
datetime: '2026-01-03T02:04:50.220711'
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
  anomaly_id: avg_response_time_1min_1767423890.220711
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 432.38917190864663
    baseline_value: 576.7964181311057
    deviation: 32.19607062569873
    severity: critical
    percentage_change: -25.03608581522699
  system_state:
    active_requests: 6
    completed_requests_1min: 829
    error_rate_1min: 0.0
    avg_response_time_1min: 432.38917190864663
  metadata: {}
  efficiency:
    requests_per_second: 13.816666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 432.39
- **Baseline Value**: 576.80
- **Deviation**: 32.20 standard deviations
- **Change**: -25.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 829
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 432.39ms

### Efficiency Metrics

- **Requests/sec**: 13.82
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 432.38917190864663,
    "baseline_value": 576.7964181311057,
    "deviation": 32.19607062569873,
    "severity": "critical",
    "percentage_change": -25.03608581522699
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 829,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 432.38917190864663
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.816666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
