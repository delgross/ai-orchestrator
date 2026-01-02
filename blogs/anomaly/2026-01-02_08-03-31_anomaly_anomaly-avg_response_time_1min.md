---
timestamp: 1767359011.503383
datetime: '2026-01-02T08:03:31.503383'
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
  anomaly_id: avg_response_time_1min_1767359011.503383
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5058.73880179032
    baseline_value: 814.5404630272429
    deviation: 29.653509153500487
    severity: critical
    percentage_change: 521.0543283496927
  system_state:
    active_requests: 2
    completed_requests_1min: 23
    error_rate_1min: 0.0
    avg_response_time_1min: 5058.73880179032
  metadata: {}
  efficiency:
    requests_per_second: 0.38333333333333336
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5058.74
- **Baseline Value**: 814.54
- **Deviation**: 29.65 standard deviations
- **Change**: +521.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 23
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 5058.74ms

### Efficiency Metrics

- **Requests/sec**: 0.38
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
    "current_value": 5058.73880179032,
    "baseline_value": 814.5404630272429,
    "deviation": 29.653509153500487,
    "severity": "critical",
    "percentage_change": 521.0543283496927
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 23,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 5058.73880179032
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.38333333333333336,
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
