---
timestamp: 1766865304.150649
datetime: '2025-12-27T14:55:04.150649'
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
  anomaly_id: requests_per_second_1766865304.150649
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.9166666666666666
    baseline_value: 2.41635
    deviation: 94.14213596404505
    severity: critical
    percentage_change: -62.06399459239486
  system_state:
    active_requests: 0
    completed_requests_1min: 55
    error_rate_1min: 0.0
    avg_response_time_1min: 23.61933101307262
  metadata: {}
  efficiency:
    requests_per_second: 0.9166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.92
- **Baseline Value**: 2.42
- **Deviation**: 94.14 standard deviations
- **Change**: -62.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 55
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 23.62ms

### Efficiency Metrics

- **Requests/sec**: 0.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.9166666666666666,
    "baseline_value": 2.41635,
    "deviation": 94.14213596404505,
    "severity": "critical",
    "percentage_change": -62.06399459239486
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 55,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 23.61933101307262
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9166666666666666,
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
