---
timestamp: 1767326773.577087
datetime: '2026-01-01T23:06:13.577087'
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
  anomaly_id: avg_response_time_1min_1767326773.577087
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 370.4565817171389
    baseline_value: 254.03623353867303
    deviation: 8.600015460264695
    severity: critical
    percentage_change: 45.828245269091774
  system_state:
    active_requests: 2
    completed_requests_1min: 111
    error_rate_1min: 0.0
    avg_response_time_1min: 370.4565817171389
  metadata: {}
  efficiency:
    requests_per_second: 1.85
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 370.46
- **Baseline Value**: 254.04
- **Deviation**: 8.60 standard deviations
- **Change**: +45.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 111
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 370.46ms

### Efficiency Metrics

- **Requests/sec**: 1.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 370.4565817171389,
    "baseline_value": 254.03623353867303,
    "deviation": 8.600015460264695,
    "severity": "critical",
    "percentage_change": 45.828245269091774
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 111,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 370.4565817171389
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
