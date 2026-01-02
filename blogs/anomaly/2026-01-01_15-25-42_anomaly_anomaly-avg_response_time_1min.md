---
timestamp: 1767299142.5718899
datetime: '2026-01-01T15:25:42.571890'
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
  anomaly_id: avg_response_time_1min_1767299142.5718899
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 13610.931118329367
    baseline_value: 1305.6397931329136
    deviation: 15.246049669231645
    severity: critical
    percentage_change: 942.4721420040066
  system_state:
    active_requests: 2
    completed_requests_1min: 12
    error_rate_1min: 0.0
    avg_response_time_1min: 13610.931118329367
  metadata: {}
  efficiency:
    requests_per_second: 0.2
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 13610.93
- **Baseline Value**: 1305.64
- **Deviation**: 15.25 standard deviations
- **Change**: +942.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 12
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 13610.93ms

### Efficiency Metrics

- **Requests/sec**: 0.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

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
    "current_value": 13610.931118329367,
    "baseline_value": 1305.6397931329136,
    "deviation": 15.246049669231645,
    "severity": "critical",
    "percentage_change": 942.4721420040066
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 12,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 13610.931118329367
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
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
