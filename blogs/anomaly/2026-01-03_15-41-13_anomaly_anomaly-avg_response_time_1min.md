---
timestamp: 1767472873.600918
datetime: '2026-01-03T15:41:13.600918'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
metadata:
  anomaly_id: avg_response_time_1min_1767472873.600918
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 8162.193059921265
    baseline_value: 0.0
    deviation: 5.084071470643035
    severity: warning
    percentage_change: 0.0
  system_state:
    active_requests: 0
    completed_requests_1min: 1
    error_rate_1min: 0.0
    avg_response_time_1min: 8162.193059921265
  metadata: {}
  efficiency:
    requests_per_second: 0.016666666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 8162.19
- **Baseline Value**: 0.00
- **Deviation**: 5.08 standard deviations
- **Change**: +0.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 1
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 8162.19ms

### Efficiency Metrics

- **Requests/sec**: 0.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 8162.193059921265,
    "baseline_value": 0.0,
    "deviation": 5.084071470643035,
    "severity": "warning",
    "percentage_change": 0.0
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 1,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 8162.193059921265
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.016666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
