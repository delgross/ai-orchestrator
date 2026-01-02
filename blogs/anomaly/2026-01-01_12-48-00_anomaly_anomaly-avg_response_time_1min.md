---
timestamp: 1767289680.834837
datetime: '2026-01-01T12:48:00.834837'
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
  anomaly_id: avg_response_time_1min_1767289680.834837
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2955.9328389167786
    baseline_value: 1162.776755857038
    deviation: 1.9521741697227433
    severity: warning
    percentage_change: 154.2132721545568
  system_state:
    active_requests: 2
    completed_requests_1min: 100
    error_rate_1min: 0.0
    avg_response_time_1min: 2955.9328389167786
  metadata: {}
  efficiency:
    requests_per_second: 1.6666666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2955.93
- **Baseline Value**: 1162.78
- **Deviation**: 1.95 standard deviations
- **Change**: +154.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 100
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2955.93ms

### Efficiency Metrics

- **Requests/sec**: 1.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 2955.9328389167786,
    "baseline_value": 1162.776755857038,
    "deviation": 1.9521741697227433,
    "severity": "warning",
    "percentage_change": 154.2132721545568
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 100,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2955.9328389167786
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6666666666666667,
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
