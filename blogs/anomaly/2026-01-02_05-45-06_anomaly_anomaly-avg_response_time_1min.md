---
timestamp: 1767350706.23554
datetime: '2026-01-02T05:45:06.235540'
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
  anomaly_id: avg_response_time_1min_1767350706.23554
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 447.86009317987947
    baseline_value: 427.6054852397729
    deviation: 8.144406007132758
    severity: critical
    percentage_change: 4.736751196900364
  system_state:
    active_requests: 7
    completed_requests_1min: 831
    error_rate_1min: 0.0
    avg_response_time_1min: 447.86009317987947
  metadata: {}
  efficiency:
    requests_per_second: 13.85
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 447.86
- **Baseline Value**: 427.61
- **Deviation**: 8.14 standard deviations
- **Change**: +4.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 831
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 447.86ms

### Efficiency Metrics

- **Requests/sec**: 13.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 447.86009317987947,
    "baseline_value": 427.6054852397729,
    "deviation": 8.144406007132758,
    "severity": "critical",
    "percentage_change": 4.736751196900364
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 831,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 447.86009317987947
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
