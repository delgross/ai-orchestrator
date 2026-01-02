---
timestamp: 1767355950.520287
datetime: '2026-01-02T07:12:30.520287'
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
  anomaly_id: avg_response_time_1min_1767355950.520287
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 8745.0476701443
    baseline_value: 814.0635588701736
    deviation: 57.87938688034135
    severity: critical
    percentage_change: 974.2463011464878
  system_state:
    active_requests: 5
    completed_requests_1min: 26
    error_rate_1min: 0.0
    avg_response_time_1min: 8745.0476701443
  metadata: {}
  efficiency:
    requests_per_second: 0.43333333333333335
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 8745.05
- **Baseline Value**: 814.06
- **Deviation**: 57.88 standard deviations
- **Change**: +974.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 26
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 8745.05ms

### Efficiency Metrics

- **Requests/sec**: 0.43
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
    "current_value": 8745.0476701443,
    "baseline_value": 814.0635588701736,
    "deviation": 57.87938688034135,
    "severity": "critical",
    "percentage_change": 974.2463011464878
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 26,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 8745.0476701443
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.43333333333333335,
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
