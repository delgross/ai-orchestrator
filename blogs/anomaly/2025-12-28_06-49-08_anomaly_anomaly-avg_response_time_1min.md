---
timestamp: 1766922548.0850601
datetime: '2025-12-28T06:49:08.085060'
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
  anomaly_id: avg_response_time_1min_1766922548.0850601
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 559.511583359515
    baseline_value: 37.86887154123823
    deviation: 6.078697734965854
    severity: critical
    percentage_change: 1377.4973760446526
  system_state:
    active_requests: 0
    completed_requests_1min: 61
    error_rate_1min: 0.0
    avg_response_time_1min: 559.511583359515
  metadata: {}
  efficiency:
    requests_per_second: 1.0166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 559.51
- **Baseline Value**: 37.87
- **Deviation**: 6.08 standard deviations
- **Change**: +1377.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 61
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 559.51ms

### Efficiency Metrics

- **Requests/sec**: 1.02
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
    "current_value": 559.511583359515,
    "baseline_value": 37.86887154123823,
    "deviation": 6.078697734965854,
    "severity": "critical",
    "percentage_change": 1377.4973760446526
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 61,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 559.511583359515
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0166666666666666,
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
