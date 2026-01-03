---
timestamp: 1767447389.538116
datetime: '2026-01-03T08:36:29.538116'
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
  anomaly_id: avg_response_time_1min_1767447389.538116
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 532.2389916909117
    baseline_value: 507.9094473652275
    deviation: 4.979041792899869
    severity: critical
    percentage_change: 4.790134235914165
  system_state:
    active_requests: 6
    completed_requests_1min: 698
    error_rate_1min: 0.0
    avg_response_time_1min: 532.2389916909117
  metadata: {}
  efficiency:
    requests_per_second: 11.633333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 532.24
- **Baseline Value**: 507.91
- **Deviation**: 4.98 standard deviations
- **Change**: +4.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 698
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 532.24ms

### Efficiency Metrics

- **Requests/sec**: 11.63
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
    "current_value": 532.2389916909117,
    "baseline_value": 507.9094473652275,
    "deviation": 4.979041792899869,
    "severity": "critical",
    "percentage_change": 4.790134235914165
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 698,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 532.2389916909117
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.633333333333333,
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
