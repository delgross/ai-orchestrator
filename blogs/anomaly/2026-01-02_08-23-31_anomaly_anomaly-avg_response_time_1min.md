---
timestamp: 1767360211.896381
datetime: '2026-01-02T08:23:31.896381'
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
  anomaly_id: avg_response_time_1min_1767360211.896381
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 7562.567538685269
    baseline_value: 814.9984614054362
    deviation: 46.71939138096491
    severity: critical
    percentage_change: 827.924149162673
  system_state:
    active_requests: 3
    completed_requests_1min: 18
    error_rate_1min: 0.0
    avg_response_time_1min: 7562.567538685269
  metadata: {}
  efficiency:
    requests_per_second: 0.3
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 7562.57
- **Baseline Value**: 815.00
- **Deviation**: 46.72 standard deviations
- **Change**: +827.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 18
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 7562.57ms

### Efficiency Metrics

- **Requests/sec**: 0.30
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

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
    "current_value": 7562.567538685269,
    "baseline_value": 814.9984614054362,
    "deviation": 46.71939138096491,
    "severity": "critical",
    "percentage_change": 827.924149162673
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 18,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 7562.567538685269
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.3,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
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
