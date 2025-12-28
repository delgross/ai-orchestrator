---
timestamp: 1766881925.244164
datetime: '2025-12-27T19:32:05.244164'
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
  anomaly_id: avg_response_time_1min_1766881925.244164
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 362.213691512307
    baseline_value: 131.69943174658596
    deviation: 10.160515900862908
    severity: critical
    percentage_change: 175.0305652109973
  system_state:
    active_requests: 0
    completed_requests_1min: 182
    error_rate_1min: 0.0
    avg_response_time_1min: 362.213691512307
  metadata: {}
  efficiency:
    requests_per_second: 3.033333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 362.21
- **Baseline Value**: 131.70
- **Deviation**: 10.16 standard deviations
- **Change**: +175.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 182
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 362.21ms

### Efficiency Metrics

- **Requests/sec**: 3.03
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
    "current_value": 362.213691512307,
    "baseline_value": 131.69943174658596,
    "deviation": 10.160515900862908,
    "severity": "critical",
    "percentage_change": 175.0305652109973
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 182,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 362.213691512307
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.033333333333333,
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
