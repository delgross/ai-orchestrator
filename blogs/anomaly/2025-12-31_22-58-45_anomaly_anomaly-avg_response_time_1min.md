---
timestamp: 1767239925.814197
datetime: '2025-12-31T22:58:45.814197'
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
  anomaly_id: avg_response_time_1min_1767239925.814197
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 109.98747223301937
    baseline_value: 168.25497534967238
    deviation: 4.824188926384978
    severity: critical
    percentage_change: -34.63047853150243
  system_state:
    active_requests: 0
    completed_requests_1min: 19
    error_rate_1min: 0.0
    avg_response_time_1min: 109.98747223301937
  metadata: {}
  efficiency:
    requests_per_second: 0.31666666666666665
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 109.99
- **Baseline Value**: 168.25
- **Deviation**: 4.82 standard deviations
- **Change**: -34.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 19
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 109.99ms

### Efficiency Metrics

- **Requests/sec**: 0.32
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
    "current_value": 109.98747223301937,
    "baseline_value": 168.25497534967238,
    "deviation": 4.824188926384978,
    "severity": "critical",
    "percentage_change": -34.63047853150243
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 19,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 109.98747223301937
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.31666666666666665,
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
