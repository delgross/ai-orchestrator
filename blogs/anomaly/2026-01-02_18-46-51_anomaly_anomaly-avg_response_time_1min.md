---
timestamp: 1767397611.131001
datetime: '2026-01-02T18:46:51.131001'
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
  anomaly_id: avg_response_time_1min_1767397611.131001
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 625.3408206136603
    baseline_value: 517.143333161419
    deviation: 3.683179053810309
    severity: critical
    percentage_change: 20.922146823551707
  system_state:
    active_requests: 6
    completed_requests_1min: 570
    error_rate_1min: 0.0
    avg_response_time_1min: 625.3408206136603
  metadata: {}
  efficiency:
    requests_per_second: 9.5
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 625.34
- **Baseline Value**: 517.14
- **Deviation**: 3.68 standard deviations
- **Change**: +20.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 570
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 625.34ms

### Efficiency Metrics

- **Requests/sec**: 9.50
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
    "current_value": 625.3408206136603,
    "baseline_value": 517.143333161419,
    "deviation": 3.683179053810309,
    "severity": "critical",
    "percentage_change": 20.922146823551707
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 570,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 625.3408206136603
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.5,
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
