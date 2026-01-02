---
timestamp: 1767353106.708655
datetime: '2026-01-02T06:25:06.708655'
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
  anomaly_id: avg_response_time_1min_1767353106.708655
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 450.11140721348613
    baseline_value: 494.1523977709588
    deviation: 3.7149009634785477
    severity: critical
    percentage_change: -8.912430812060094
  system_state:
    active_requests: 6
    completed_requests_1min: 832
    error_rate_1min: 0.0
    avg_response_time_1min: 450.11140721348613
  metadata: {}
  efficiency:
    requests_per_second: 13.866666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 450.11
- **Baseline Value**: 494.15
- **Deviation**: 3.71 standard deviations
- **Change**: -8.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 832
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 450.11ms

### Efficiency Metrics

- **Requests/sec**: 13.87
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
    "current_value": 450.11140721348613,
    "baseline_value": 494.1523977709588,
    "deviation": 3.7149009634785477,
    "severity": "critical",
    "percentage_change": -8.912430812060094
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 832,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 450.11140721348613
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.866666666666667,
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
