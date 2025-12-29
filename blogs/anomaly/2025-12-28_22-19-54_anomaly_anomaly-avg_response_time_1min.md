---
timestamp: 1766978394.045892
datetime: '2025-12-28T22:19:54.045892'
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
  anomaly_id: avg_response_time_1min_1766978394.045892
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 496.44686007986263
    baseline_value: 167.52271411098687
    deviation: 4.393740146646631
    severity: warning
    percentage_change: 196.34599863929944
  system_state:
    active_requests: 1
    completed_requests_1min: 98
    error_rate_1min: 0.0
    avg_response_time_1min: 496.44686007986263
  metadata: {}
  efficiency:
    requests_per_second: 1.6333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 496.45
- **Baseline Value**: 167.52
- **Deviation**: 4.39 standard deviations
- **Change**: +196.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 98
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 496.45ms

### Efficiency Metrics

- **Requests/sec**: 1.63
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
    "current_value": 496.44686007986263,
    "baseline_value": 167.52271411098687,
    "deviation": 4.393740146646631,
    "severity": "warning",
    "percentage_change": 196.34599863929944
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 98,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 496.44686007986263
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6333333333333333,
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
