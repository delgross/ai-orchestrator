---
timestamp: 1767401759.530352
datetime: '2026-01-02T19:55:59.530352'
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
  anomaly_id: avg_response_time_1min_1767401759.530352
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 641.46774507338
    baseline_value: 286.21837165620593
    deviation: 20.264677476877164
    severity: critical
    percentage_change: 124.1182986827573
  system_state:
    active_requests: 1
    completed_requests_1min: 155
    error_rate_1min: 0.0
    avg_response_time_1min: 641.46774507338
  metadata: {}
  efficiency:
    requests_per_second: 2.5833333333333335
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 641.47
- **Baseline Value**: 286.22
- **Deviation**: 20.26 standard deviations
- **Change**: +124.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 155
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 641.47ms

### Efficiency Metrics

- **Requests/sec**: 2.58
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

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
    "current_value": 641.46774507338,
    "baseline_value": 286.21837165620593,
    "deviation": 20.264677476877164,
    "severity": "critical",
    "percentage_change": 124.1182986827573
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 155,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 641.46774507338
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.5833333333333335,
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
3. Investigate immediately - critical system issue detected
