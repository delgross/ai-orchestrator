---
timestamp: 1767325265.931135
datetime: '2026-01-01T22:41:05.931135'
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
  anomaly_id: avg_response_time_1min_1767325265.931135
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 967.5009250640869
    baseline_value: 447.165959255657
    deviation: 80.69529633736184
    severity: critical
    percentage_change: 116.36283018380209
  system_state:
    active_requests: 1
    completed_requests_1min: 3
    error_rate_1min: 0.0
    avg_response_time_1min: 967.5009250640869
  metadata: {}
  efficiency:
    requests_per_second: 0.05
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 967.50
- **Baseline Value**: 447.17
- **Deviation**: 80.70 standard deviations
- **Change**: +116.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 3
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 967.50ms

### Efficiency Metrics

- **Requests/sec**: 0.05
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
    "current_value": 967.5009250640869,
    "baseline_value": 447.165959255657,
    "deviation": 80.69529633736184,
    "severity": "critical",
    "percentage_change": 116.36283018380209
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 3,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 967.5009250640869
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.05,
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
