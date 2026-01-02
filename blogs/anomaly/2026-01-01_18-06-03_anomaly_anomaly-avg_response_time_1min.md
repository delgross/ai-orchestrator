---
timestamp: 1767308763.356009
datetime: '2026-01-01T18:06:03.356009'
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
  anomaly_id: avg_response_time_1min_1767308763.356009
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 795.7052383979742
    baseline_value: 298.8822537709058
    deviation: 11.879616357313072
    severity: critical
    percentage_change: 166.22699352631517
  system_state:
    active_requests: 3
    completed_requests_1min: 137
    error_rate_1min: 0.0
    avg_response_time_1min: 795.7052383979742
  metadata: {}
  efficiency:
    requests_per_second: 2.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 795.71
- **Baseline Value**: 298.88
- **Deviation**: 11.88 standard deviations
- **Change**: +166.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 137
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 795.71ms

### Efficiency Metrics

- **Requests/sec**: 2.28
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
    "current_value": 795.7052383979742,
    "baseline_value": 298.8822537709058,
    "deviation": 11.879616357313072,
    "severity": "critical",
    "percentage_change": 166.22699352631517
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 137,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 795.7052383979742
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.283333333333333,
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
