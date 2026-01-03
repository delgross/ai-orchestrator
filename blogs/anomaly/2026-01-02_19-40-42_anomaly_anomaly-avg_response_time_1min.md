---
timestamp: 1767400842.7204108
datetime: '2026-01-02T19:40:42.720411'
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
  anomaly_id: avg_response_time_1min_1767400842.7204108
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1422.354354577906
    baseline_value: 396.12770453095436
    deviation: 18.233291058030517
    severity: critical
    percentage_change: 259.0645991958787
  system_state:
    active_requests: 6
    completed_requests_1min: 170
    error_rate_1min: 0.0
    avg_response_time_1min: 1422.354354577906
  metadata: {}
  efficiency:
    requests_per_second: 2.8333333333333335
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1422.35
- **Baseline Value**: 396.13
- **Deviation**: 18.23 standard deviations
- **Change**: +259.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 170
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1422.35ms

### Efficiency Metrics

- **Requests/sec**: 2.83
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

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
    "current_value": 1422.354354577906,
    "baseline_value": 396.12770453095436,
    "deviation": 18.233291058030517,
    "severity": "critical",
    "percentage_change": 259.0645991958787
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 170,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1422.354354577906
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.8333333333333335,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
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
