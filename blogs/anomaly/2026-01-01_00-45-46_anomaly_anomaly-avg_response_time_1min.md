---
timestamp: 1767246346.4396951
datetime: '2026-01-01T00:45:46.439695'
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
  anomaly_id: avg_response_time_1min_1767246346.4396951
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 239.87770465112501
    baseline_value: 180.53401691812866
    deviation: 3.2280885444254204
    severity: critical
    percentage_change: 32.87119444082854
  system_state:
    active_requests: 0
    completed_requests_1min: 62
    error_rate_1min: 0.0
    avg_response_time_1min: 239.87770465112501
  metadata: {}
  efficiency:
    requests_per_second: 1.0333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 239.88
- **Baseline Value**: 180.53
- **Deviation**: 3.23 standard deviations
- **Change**: +32.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 62
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 239.88ms

### Efficiency Metrics

- **Requests/sec**: 1.03
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
    "current_value": 239.87770465112501,
    "baseline_value": 180.53401691812866,
    "deviation": 3.2280885444254204,
    "severity": "critical",
    "percentage_change": 32.87119444082854
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 62,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 239.87770465112501
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0333333333333334,
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
