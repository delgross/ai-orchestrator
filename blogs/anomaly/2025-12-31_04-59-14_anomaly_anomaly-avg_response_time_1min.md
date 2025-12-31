---
timestamp: 1767175154.213483
datetime: '2025-12-31T04:59:14.213483'
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
  anomaly_id: avg_response_time_1min_1767175154.213483
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 397.733445753131
    baseline_value: 166.43750667572021
    deviation: 4.5535001441261125
    severity: critical
    percentage_change: 138.96863975982168
  system_state:
    active_requests: 2
    completed_requests_1min: 57
    error_rate_1min: 0.0
    avg_response_time_1min: 397.733445753131
  metadata: {}
  efficiency:
    requests_per_second: 0.95
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 397.73
- **Baseline Value**: 166.44
- **Deviation**: 4.55 standard deviations
- **Change**: +139.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 57
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 397.73ms

### Efficiency Metrics

- **Requests/sec**: 0.95
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
    "current_value": 397.733445753131,
    "baseline_value": 166.43750667572021,
    "deviation": 4.5535001441261125,
    "severity": "critical",
    "percentage_change": 138.96863975982168
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 57,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 397.733445753131
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.95,
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
