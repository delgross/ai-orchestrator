---
timestamp: 1767364289.8199182
datetime: '2026-01-02T09:31:29.819918'
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
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767364289.8199182
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 216378.13085317612
    baseline_value: 60057.64722824097
    deviation: 3.0403873271143627
    severity: critical
    percentage_change: 260.284061796261
  system_state:
    active_requests: 7
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 216378.13085317612
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 216378.13
- **Baseline Value**: 60057.65
- **Deviation**: 3.04 standard deviations
- **Change**: +260.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 216378.13ms

### Efficiency Metrics

- **Requests/sec**: 0.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 216378.13085317612,
    "baseline_value": 60057.64722824097,
    "deviation": 3.0403873271143627,
    "severity": "critical",
    "percentage_change": 260.284061796261
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 216378.13085317612
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected
