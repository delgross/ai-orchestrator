---
timestamp: 1767359611.699012
datetime: '2026-01-02T08:13:31.699012'
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
  anomaly_id: avg_response_time_1min_1767359611.699012
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 6864.424502408063
    baseline_value: 814.6027039275189
    deviation: 42.12714196099016
    severity: critical
    percentage_change: 742.6714604938066
  system_state:
    active_requests: 2
    completed_requests_1min: 27
    error_rate_1min: 0.0
    avg_response_time_1min: 6864.424502408063
  metadata: {}
  efficiency:
    requests_per_second: 0.45
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 6864.42
- **Baseline Value**: 814.60
- **Deviation**: 42.13 standard deviations
- **Change**: +742.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 27
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 6864.42ms

### Efficiency Metrics

- **Requests/sec**: 0.45
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
    "current_value": 6864.424502408063,
    "baseline_value": 814.6027039275189,
    "deviation": 42.12714196099016,
    "severity": "critical",
    "percentage_change": 742.6714604938066
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 27,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 6864.424502408063
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.45,
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
