---
timestamp: 1767152584.5024152
datetime: '2025-12-30T22:43:04.502415'
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
  anomaly_id: avg_response_time_1min_1767152584.5024152
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 110.69814885248903
    baseline_value: 85.23501210267159
    deviation: 8.942196653927688
    severity: critical
    percentage_change: 29.87403429842339
  system_state:
    active_requests: 0
    completed_requests_1min: 122
    error_rate_1min: 0.0
    avg_response_time_1min: 110.69814885248903
  metadata: {}
  efficiency:
    requests_per_second: 2.033333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 110.70
- **Baseline Value**: 85.24
- **Deviation**: 8.94 standard deviations
- **Change**: +29.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 122
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 110.70ms

### Efficiency Metrics

- **Requests/sec**: 2.03
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
    "current_value": 110.69814885248903,
    "baseline_value": 85.23501210267159,
    "deviation": 8.942196653927688,
    "severity": "critical",
    "percentage_change": 29.87403429842339
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 122,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 110.69814885248903
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.033333333333333,
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
