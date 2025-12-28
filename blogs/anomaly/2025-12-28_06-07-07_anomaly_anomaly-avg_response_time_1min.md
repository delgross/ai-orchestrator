---
timestamp: 1766920027.943753
datetime: '2025-12-28T06:07:07.943753'
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
  anomaly_id: avg_response_time_1min_1766920027.943753
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 140.98095509313768
    baseline_value: 24.1442818943801
    deviation: 4.1457387260620076
    severity: warning
    percentage_change: 483.91032588943085
  system_state:
    active_requests: 1
    completed_requests_1min: 62
    error_rate_1min: 0.0
    avg_response_time_1min: 140.98095509313768
  metadata: {}
  efficiency:
    requests_per_second: 1.0333333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 140.98
- **Baseline Value**: 24.14
- **Deviation**: 4.15 standard deviations
- **Change**: +483.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 62
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 140.98ms

### Efficiency Metrics

- **Requests/sec**: 1.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 140.98095509313768,
    "baseline_value": 24.1442818943801,
    "deviation": 4.1457387260620076,
    "severity": "warning",
    "percentage_change": 483.91032588943085
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 62,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 140.98095509313768
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
