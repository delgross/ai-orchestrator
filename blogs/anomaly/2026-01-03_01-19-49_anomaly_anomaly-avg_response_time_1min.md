---
timestamp: 1767421189.444909
datetime: '2026-01-03T01:19:49.444909'
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
  anomaly_id: avg_response_time_1min_1767421189.444909
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 347.07054897626887
    baseline_value: 428.1885623931885
    deviation: 3.389738626008014
    severity: critical
    percentage_change: -18.94446058146508
  system_state:
    active_requests: 15
    completed_requests_1min: 2455
    error_rate_1min: 0.0
    avg_response_time_1min: 347.07054897626887
  metadata: {}
  efficiency:
    requests_per_second: 40.916666666666664
    cache_hit_rate: 0.0
    queue_depth: 15
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 347.07
- **Baseline Value**: 428.19
- **Deviation**: 3.39 standard deviations
- **Change**: -18.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 15
- **Completed Requests (1min)**: 2455
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 347.07ms

### Efficiency Metrics

- **Requests/sec**: 40.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 15

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 347.07054897626887,
    "baseline_value": 428.1885623931885,
    "deviation": 3.389738626008014,
    "severity": "critical",
    "percentage_change": -18.94446058146508
  },
  "system_state": {
    "active_requests": 15,
    "completed_requests_1min": 2455,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 347.07054897626887
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 40.916666666666664,
    "cache_hit_rate": 0.0,
    "queue_depth": 15
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
