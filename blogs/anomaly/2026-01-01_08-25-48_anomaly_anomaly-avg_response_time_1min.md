---
timestamp: 1767273948.63595
datetime: '2026-01-01T08:25:48.635950'
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
  anomaly_id: avg_response_time_1min_1767273948.63595
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 918.4499492107982
    baseline_value: 330.4986733656663
    deviation: 6.904702970979463
    severity: critical
    percentage_change: 177.89822568958334
  system_state:
    active_requests: 0
    completed_requests_1min: 71
    error_rate_1min: 0.0
    avg_response_time_1min: 918.4499492107982
  metadata: {}
  efficiency:
    requests_per_second: 1.1833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 918.45
- **Baseline Value**: 330.50
- **Deviation**: 6.90 standard deviations
- **Change**: +177.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 71
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 918.45ms

### Efficiency Metrics

- **Requests/sec**: 1.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

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
    "current_value": 918.4499492107982,
    "baseline_value": 330.4986733656663,
    "deviation": 6.904702970979463,
    "severity": "critical",
    "percentage_change": 177.89822568958334
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 71,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 918.4499492107982
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
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
