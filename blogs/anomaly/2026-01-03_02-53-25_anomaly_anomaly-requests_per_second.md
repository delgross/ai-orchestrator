---
timestamp: 1767426805.1821299
datetime: '2026-01-03T02:53:25.182130'
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
  anomaly_id: requests_per_second_1767426805.1821299
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.066666666666666
    baseline_value: 11.4
    deviation: 4.000000000000064
    severity: critical
    percentage_change: -2.9239766081871394
  system_state:
    active_requests: 6
    completed_requests_1min: 664
    error_rate_1min: 0.0
    avg_response_time_1min: 551.5127778053284
  metadata: {}
  efficiency:
    requests_per_second: 11.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.07
- **Baseline Value**: 11.40
- **Deviation**: 4.00 standard deviations
- **Change**: -2.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 664
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 551.51ms

### Efficiency Metrics

- **Requests/sec**: 11.07
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
    "current_value": 11.066666666666666,
    "baseline_value": 11.4,
    "deviation": 4.000000000000064,
    "severity": "critical",
    "percentage_change": -2.9239766081871394
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 664,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 551.5127778053284
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.066666666666666,
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
