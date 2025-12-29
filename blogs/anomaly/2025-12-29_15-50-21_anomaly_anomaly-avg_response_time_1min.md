---
timestamp: 1767041421.692183
datetime: '2025-12-29T15:50:21.692183'
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
  anomaly_id: avg_response_time_1min_1767041421.692183
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 25695.116877555847
    baseline_value: 775.9074335143821
    deviation: 5.3376529592156965
    severity: warning
    percentage_change: 3211.621434166808
  system_state:
    active_requests: 4
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 25695.116877555847
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 25695.12
- **Baseline Value**: 775.91
- **Deviation**: 5.34 standard deviations
- **Change**: +3211.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 25695.12ms

### Efficiency Metrics

- **Requests/sec**: 0.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 25695.116877555847,
    "baseline_value": 775.9074335143821,
    "deviation": 5.3376529592156965,
    "severity": "warning",
    "percentage_change": 3211.621434166808
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 25695.116877555847
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
