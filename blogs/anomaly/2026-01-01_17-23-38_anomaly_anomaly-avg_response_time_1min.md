---
timestamp: 1767306218.188752
datetime: '2026-01-01T17:23:38.188752'
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
  anomaly_id: avg_response_time_1min_1767306218.188752
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 184.96081296433795
    baseline_value: 543.6449354887009
    deviation: 4.541714185602583
    severity: critical
    percentage_change: -65.97764443476873
  system_state:
    active_requests: 4
    completed_requests_1min: 376
    error_rate_1min: 0.0
    avg_response_time_1min: 184.96081296433795
  metadata: {}
  efficiency:
    requests_per_second: 6.266666666666667
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 184.96
- **Baseline Value**: 543.64
- **Deviation**: 4.54 standard deviations
- **Change**: -66.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 376
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 184.96ms

### Efficiency Metrics

- **Requests/sec**: 6.27
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 184.96081296433795,
    "baseline_value": 543.6449354887009,
    "deviation": 4.541714185602583,
    "severity": "critical",
    "percentage_change": -65.97764443476873
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 376,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 184.96081296433795
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.266666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
