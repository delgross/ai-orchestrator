---
timestamp: 1766985654.577693
datetime: '2025-12-29T00:20:54.577693'
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
  anomaly_id: avg_response_time_1min_1766985654.577693
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 250.94931190078324
    baseline_value: 152.5800851365442
    deviation: 6.500298341828225
    severity: critical
    percentage_change: 64.4705543821189
  system_state:
    active_requests: 1
    completed_requests_1min: 111
    error_rate_1min: 0.0
    avg_response_time_1min: 250.94931190078324
  metadata: {}
  efficiency:
    requests_per_second: 1.85
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 250.95
- **Baseline Value**: 152.58
- **Deviation**: 6.50 standard deviations
- **Change**: +64.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 111
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 250.95ms

### Efficiency Metrics

- **Requests/sec**: 1.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 250.94931190078324,
    "baseline_value": 152.5800851365442,
    "deviation": 6.500298341828225,
    "severity": "critical",
    "percentage_change": 64.4705543821189
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 111,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 250.94931190078324
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
