---
timestamp: 1767395570.676896
datetime: '2026-01-02T18:12:50.676896'
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
  anomaly_id: requests_per_second_1767395570.676896
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.183333333333334
    baseline_value: 13.266666666666667
    deviation: 8.854166666666679
    severity: critical
    percentage_change: -53.39195979899498
  system_state:
    active_requests: 6
    completed_requests_1min: 371
    error_rate_1min: 0.0
    avg_response_time_1min: 967.6422481588277
  metadata: {}
  efficiency:
    requests_per_second: 6.183333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.18
- **Baseline Value**: 13.27
- **Deviation**: 8.85 standard deviations
- **Change**: -53.4%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 371
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 967.64ms

### Efficiency Metrics

- **Requests/sec**: 6.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.183333333333334,
    "baseline_value": 13.266666666666667,
    "deviation": 8.854166666666679,
    "severity": "critical",
    "percentage_change": -53.39195979899498
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 371,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 967.6422481588277
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.183333333333334,
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
