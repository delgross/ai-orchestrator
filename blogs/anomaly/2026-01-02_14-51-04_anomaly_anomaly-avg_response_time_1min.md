---
timestamp: 1767383464.516194
datetime: '2026-01-02T14:51:04.516194'
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
  anomaly_id: avg_response_time_1min_1767383464.516194
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 43043.748915195465
    baseline_value: 765.8302913954917
    deviation: 1327.9861992789681
    severity: critical
    percentage_change: 5520.533608922858
  system_state:
    active_requests: 5
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 43043.748915195465
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 43043.75
- **Baseline Value**: 765.83
- **Deviation**: 1327.99 standard deviations
- **Change**: +5520.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 43043.75ms

### Efficiency Metrics

- **Requests/sec**: 0.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 5

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
    "current_value": 43043.748915195465,
    "baseline_value": 765.8302913954917,
    "deviation": 1327.9861992789681,
    "severity": "critical",
    "percentage_change": 5520.533608922858
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 43043.748915195465
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
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
3. Investigate immediately - critical system issue detected
