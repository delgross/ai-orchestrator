---
timestamp: 1767410024.758833
datetime: '2026-01-02T22:13:44.758833'
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
  anomaly_id: avg_response_time_1min_1767410024.758833
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4695.004065831502
    baseline_value: 1338.8207112589191
    deviation: 2.506820611862733
    severity: warning
    percentage_change: 250.68206118627333
  system_state:
    active_requests: 1
    completed_requests_1min: 3
    error_rate_1min: 0.0
    avg_response_time_1min: 4695.004065831502
  metadata: {}
  efficiency:
    requests_per_second: 0.05
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4695.00
- **Baseline Value**: 1338.82
- **Deviation**: 2.51 standard deviations
- **Change**: +250.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 3
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4695.00ms

### Efficiency Metrics

- **Requests/sec**: 0.05
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
    "current_value": 4695.004065831502,
    "baseline_value": 1338.8207112589191,
    "deviation": 2.506820611862733,
    "severity": "warning",
    "percentage_change": 250.68206118627333
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 3,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4695.004065831502
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.05,
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
