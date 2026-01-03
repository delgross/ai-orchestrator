---
timestamp: 1767459695.269153
datetime: '2026-01-03T12:01:35.269153'
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
  anomaly_id: avg_response_time_1min_1767459695.269153
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1807.3792627879552
    baseline_value: 576.1915677553648
    deviation: 5.018682430207778
    severity: critical
    percentage_change: 213.6767984697963
  system_state:
    active_requests: 0
    completed_requests_1min: 14
    error_rate_1min: 0.0
    avg_response_time_1min: 1807.3792627879552
  metadata: {}
  efficiency:
    requests_per_second: 0.23333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1807.38
- **Baseline Value**: 576.19
- **Deviation**: 5.02 standard deviations
- **Change**: +213.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 14
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1807.38ms

### Efficiency Metrics

- **Requests/sec**: 0.23
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
    "current_value": 1807.3792627879552,
    "baseline_value": 576.1915677553648,
    "deviation": 5.018682430207778,
    "severity": "critical",
    "percentage_change": 213.6767984697963
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 14,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1807.3792627879552
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.23333333333333334,
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
