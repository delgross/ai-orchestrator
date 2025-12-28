---
timestamp: 1766841500.044208
datetime: '2025-12-27T08:18:20.044208'
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
  anomaly_id: avg_response_time_1min_1766841500.044208
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 15.40288521611611
    baseline_value: 6.279984091304274
    deviation: 4.237793328788436
    severity: warning
    percentage_change: 145.26949419257406
  system_state:
    active_requests: 0
    completed_requests_1min: 449
    error_rate_1min: 0.0
    avg_response_time_1min: 15.40288521611611
  metadata: {}
  efficiency:
    requests_per_second: 7.483333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 15.40
- **Baseline Value**: 6.28
- **Deviation**: 4.24 standard deviations
- **Change**: +145.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 449
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 15.40ms

### Efficiency Metrics

- **Requests/sec**: 7.48
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
    "current_value": 15.40288521611611,
    "baseline_value": 6.279984091304274,
    "deviation": 4.237793328788436,
    "severity": "warning",
    "percentage_change": 145.26949419257406
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 449,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 15.40288521611611
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.483333333333333,
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
