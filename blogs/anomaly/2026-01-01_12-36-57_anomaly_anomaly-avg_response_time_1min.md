---
timestamp: 1767289017.595645
datetime: '2026-01-01T12:36:57.595645'
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
  anomaly_id: avg_response_time_1min_1767289017.595645
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 500.42642827806526
    baseline_value: 177.33902161249696
    deviation: 5.912599466348938
    severity: critical
    percentage_change: 182.186302669215
  system_state:
    active_requests: 2
    completed_requests_1min: 179
    error_rate_1min: 0.0
    avg_response_time_1min: 500.42642827806526
  metadata: {}
  efficiency:
    requests_per_second: 2.9833333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 500.43
- **Baseline Value**: 177.34
- **Deviation**: 5.91 standard deviations
- **Change**: +182.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 179
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 500.43ms

### Efficiency Metrics

- **Requests/sec**: 2.98
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
    "current_value": 500.42642827806526,
    "baseline_value": 177.33902161249696,
    "deviation": 5.912599466348938,
    "severity": "critical",
    "percentage_change": 182.186302669215
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 179,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 500.42642827806526
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.9833333333333334,
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
