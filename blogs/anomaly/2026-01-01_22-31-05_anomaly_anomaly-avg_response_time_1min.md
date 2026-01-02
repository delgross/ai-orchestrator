---
timestamp: 1767324665.814076
datetime: '2026-01-01T22:31:05.814076'
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
  anomaly_id: avg_response_time_1min_1767324665.814076
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 871.3830471038818
    baseline_value: 446.85324248421955
    deviation: 57.35501796913355
    severity: critical
    percentage_change: 95.00430214169351
  system_state:
    active_requests: 0
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 871.3830471038818
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 871.38
- **Baseline Value**: 446.85
- **Deviation**: 57.36 standard deviations
- **Change**: +95.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 871.38ms

### Efficiency Metrics

- **Requests/sec**: 0.08
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
    "current_value": 871.3830471038818,
    "baseline_value": 446.85324248421955,
    "deviation": 57.35501796913355,
    "severity": "critical",
    "percentage_change": 95.00430214169351
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 871.3830471038818
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
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
