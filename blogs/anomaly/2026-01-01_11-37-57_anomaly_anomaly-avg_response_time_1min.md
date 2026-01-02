---
timestamp: 1767285477.065359
datetime: '2026-01-01T11:37:57.065359'
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
  anomaly_id: avg_response_time_1min_1767285477.065359
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 877.3995608818241
    baseline_value: 416.77358709735637
    deviation: 1.6867536757059431
    severity: warning
    percentage_change: 110.52187279729597
  system_state:
    active_requests: 5
    completed_requests_1min: 82
    error_rate_1min: 0.0
    avg_response_time_1min: 877.3995608818241
  metadata: {}
  efficiency:
    requests_per_second: 1.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 877.40
- **Baseline Value**: 416.77
- **Deviation**: 1.69 standard deviations
- **Change**: +110.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 82
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 877.40ms

### Efficiency Metrics

- **Requests/sec**: 1.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 5

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 877.3995608818241,
    "baseline_value": 416.77358709735637,
    "deviation": 1.6867536757059431,
    "severity": "warning",
    "percentage_change": 110.52187279729597
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 82,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 877.3995608818241
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 5
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
