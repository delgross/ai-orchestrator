---
timestamp: 1767381963.968102
datetime: '2026-01-02T14:26:03.968102'
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
  anomaly_id: avg_response_time_1min_1767381963.968102
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1093.3072078094053
    baseline_value: 635.2176965843321
    deviation: 6.933979366032757
    severity: critical
    percentage_change: 72.1153572528433
  system_state:
    active_requests: 9
    completed_requests_1min: 712
    error_rate_1min: 0.0
    avg_response_time_1min: 1093.3072078094053
  metadata: {}
  efficiency:
    requests_per_second: 11.866666666666667
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1093.31
- **Baseline Value**: 635.22
- **Deviation**: 6.93 standard deviations
- **Change**: +72.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 712
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1093.31ms

### Efficiency Metrics

- **Requests/sec**: 11.87
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1093.3072078094053,
    "baseline_value": 635.2176965843321,
    "deviation": 6.933979366032757,
    "severity": "critical",
    "percentage_change": 72.1153572528433
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 712,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1093.3072078094053
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.866666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
