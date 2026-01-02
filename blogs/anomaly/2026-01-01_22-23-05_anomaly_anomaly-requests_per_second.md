---
timestamp: 1767324185.740406
datetime: '2026-01-01T22:23:05.740406'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767324185.740406
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.75
    baseline_value: 13.35
    deviation: 6.000000000000027
    severity: critical
    percentage_change: 2.996254681647943
  system_state:
    active_requests: 6
    completed_requests_1min: 825
    error_rate_1min: 0.0
    avg_response_time_1min: 442.01434713421446
  metadata: {}
  efficiency:
    requests_per_second: 13.75
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.75
- **Baseline Value**: 13.35
- **Deviation**: 6.00 standard deviations
- **Change**: +3.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 825
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 442.01ms

### Efficiency Metrics

- **Requests/sec**: 13.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.75,
    "baseline_value": 13.35,
    "deviation": 6.000000000000027,
    "severity": "critical",
    "percentage_change": 2.996254681647943
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 825,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 442.01434713421446
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.75,
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
