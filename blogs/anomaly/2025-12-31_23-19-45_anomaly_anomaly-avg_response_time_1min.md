---
timestamp: 1767241185.9239628
datetime: '2025-12-31T23:19:45.923963'
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
  anomaly_id: avg_response_time_1min_1767241185.9239628
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2527.0380154252052
    baseline_value: 186.08114404498406
    deviation: 128.8622322878503
    severity: critical
    percentage_change: 1258.030137010716
  system_state:
    active_requests: 0
    completed_requests_1min: 64
    error_rate_1min: 0.0
    avg_response_time_1min: 2527.0380154252052
  metadata: {}
  efficiency:
    requests_per_second: 1.0666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2527.04
- **Baseline Value**: 186.08
- **Deviation**: 128.86 standard deviations
- **Change**: +1258.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 64
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2527.04ms

### Efficiency Metrics

- **Requests/sec**: 1.07
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
    "current_value": 2527.0380154252052,
    "baseline_value": 186.08114404498406,
    "deviation": 128.8622322878503,
    "severity": "critical",
    "percentage_change": 1258.030137010716
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 64,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2527.0380154252052
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0666666666666667,
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
