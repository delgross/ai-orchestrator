---
timestamp: 1767289440.82185
datetime: '2026-01-01T12:44:00.821850'
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
  anomaly_id: avg_response_time_1min_1767289440.82185
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1162.7681684923602
    baseline_value: 312.63222647648234
    deviation: 4.539053464546075
    severity: critical
    percentage_change: 271.9284417979952
  system_state:
    active_requests: 2
    completed_requests_1min: 111
    error_rate_1min: 0.0
    avg_response_time_1min: 1162.7681684923602
  metadata: {}
  efficiency:
    requests_per_second: 1.85
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1162.77
- **Baseline Value**: 312.63
- **Deviation**: 4.54 standard deviations
- **Change**: +271.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 111
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1162.77ms

### Efficiency Metrics

- **Requests/sec**: 1.85
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
    "current_value": 1162.7681684923602,
    "baseline_value": 312.63222647648234,
    "deviation": 4.539053464546075,
    "severity": "critical",
    "percentage_change": 271.9284417979952
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 111,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1162.7681684923602
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.85,
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
