---
timestamp: 1767286017.075966
datetime: '2026-01-01T11:46:57.075966'
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
  anomaly_id: avg_response_time_1min_1767286017.075966
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2339.3793716663267
    baseline_value: 931.8170176612007
    deviation: 1.8426997899295867
    severity: warning
    percentage_change: 151.05566085689387
  system_state:
    active_requests: 2
    completed_requests_1min: 82
    error_rate_1min: 0.0
    avg_response_time_1min: 2339.3793716663267
  metadata: {}
  efficiency:
    requests_per_second: 1.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2339.38
- **Baseline Value**: 931.82
- **Deviation**: 1.84 standard deviations
- **Change**: +151.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 82
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2339.38ms

### Efficiency Metrics

- **Requests/sec**: 1.37
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
    "current_value": 2339.3793716663267,
    "baseline_value": 931.8170176612007,
    "deviation": 1.8426997899295867,
    "severity": "warning",
    "percentage_change": 151.05566085689387
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 82,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2339.3793716663267
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3666666666666667,
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
