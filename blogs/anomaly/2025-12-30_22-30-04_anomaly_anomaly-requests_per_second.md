---
timestamp: 1767151804.426731
datetime: '2025-12-30T22:30:04.426731'
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
  anomaly_id: requests_per_second_1767151804.426731
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 22.466666666666665
    baseline_value: 20.433333333333334
    deviation: 30.50000000000008
    severity: critical
    percentage_change: 9.951060358890693
  system_state:
    active_requests: 1
    completed_requests_1min: 1348
    error_rate_1min: 0.0
    avg_response_time_1min: 86.8080702309085
  metadata: {}
  efficiency:
    requests_per_second: 22.466666666666665
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 22.47
- **Baseline Value**: 20.43
- **Deviation**: 30.50 standard deviations
- **Change**: +10.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 1348
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 86.81ms

### Efficiency Metrics

- **Requests/sec**: 22.47
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
    "current_value": 22.466666666666665,
    "baseline_value": 20.433333333333334,
    "deviation": 30.50000000000008,
    "severity": "critical",
    "percentage_change": 9.951060358890693
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 1348,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 86.8080702309085
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 22.466666666666665,
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
