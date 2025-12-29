---
timestamp: 1766987454.710397
datetime: '2025-12-29T00:50:54.710397'
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
  anomaly_id: avg_response_time_1min_1766987454.710397
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 251.4548493969825
    baseline_value: 155.85269349541198
    deviation: 6.39927671010642
    severity: critical
    percentage_change: 61.34135622390438
  system_state:
    active_requests: 0
    completed_requests_1min: 124
    error_rate_1min: 0.0
    avg_response_time_1min: 251.4548493969825
  metadata: {}
  efficiency:
    requests_per_second: 2.066666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 251.45
- **Baseline Value**: 155.85
- **Deviation**: 6.40 standard deviations
- **Change**: +61.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 124
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 251.45ms

### Efficiency Metrics

- **Requests/sec**: 2.07
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
    "current_value": 251.4548493969825,
    "baseline_value": 155.85269349541198,
    "deviation": 6.39927671010642,
    "severity": "critical",
    "percentage_change": 61.34135622390438
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 124,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 251.4548493969825
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.066666666666667,
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
