---
timestamp: 1767310804.419945
datetime: '2026-01-01T18:40:04.419945'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767310804.419945
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.416666666666667
    baseline_value: 2.033333333333333
    deviation: 6.414634146341466
    severity: critical
    percentage_change: 215.57377049180332
  system_state:
    active_requests: 1
    completed_requests_1min: 385
    error_rate_1min: 0.0
    avg_response_time_1min: 220.15351196388144
  metadata: {}
  efficiency:
    requests_per_second: 6.416666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.42
- **Baseline Value**: 2.03
- **Deviation**: 6.41 standard deviations
- **Change**: +215.6%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 385
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 220.15ms

### Efficiency Metrics

- **Requests/sec**: 6.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.416666666666667,
    "baseline_value": 2.033333333333333,
    "deviation": 6.414634146341466,
    "severity": "critical",
    "percentage_change": 215.57377049180332
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 385,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 220.15351196388144
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.416666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
