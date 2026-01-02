---
timestamp: 1767352026.587831
datetime: '2026-01-02T06:07:06.587831'
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
  anomaly_id: requests_per_second_1767352026.587831
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.2
    baseline_value: 13.616666666666667
    deviation: 3.5714285714286214
    severity: critical
    percentage_change: -3.059975520195847
  system_state:
    active_requests: 7
    completed_requests_1min: 792
    error_rate_1min: 0.0
    avg_response_time_1min: 498.2847207122379
  metadata: {}
  efficiency:
    requests_per_second: 13.2
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.20
- **Baseline Value**: 13.62
- **Deviation**: 3.57 standard deviations
- **Change**: -3.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 792
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 498.28ms

### Efficiency Metrics

- **Requests/sec**: 13.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.2,
    "baseline_value": 13.616666666666667,
    "deviation": 3.5714285714286214,
    "severity": "critical",
    "percentage_change": -3.059975520195847
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 792,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 498.2847207122379
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.2,
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
