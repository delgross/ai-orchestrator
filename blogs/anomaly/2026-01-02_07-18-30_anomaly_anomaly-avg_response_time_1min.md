---
timestamp: 1767356310.667371
datetime: '2026-01-02T07:18:30.667371'
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
  anomaly_id: avg_response_time_1min_1767356310.667371
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2109.5691323280334
    baseline_value: 814.1458387374878
    deviation: 9.406622551438256
    severity: critical
    percentage_change: 159.1144033358181
  system_state:
    active_requests: 4
    completed_requests_1min: 120
    error_rate_1min: 0.0
    avg_response_time_1min: 2109.5691323280334
  metadata: {}
  efficiency:
    requests_per_second: 2.0
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2109.57
- **Baseline Value**: 814.15
- **Deviation**: 9.41 standard deviations
- **Change**: +159.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 120
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2109.57ms

### Efficiency Metrics

- **Requests/sec**: 2.00
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

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
    "current_value": 2109.5691323280334,
    "baseline_value": 814.1458387374878,
    "deviation": 9.406622551438256,
    "severity": "critical",
    "percentage_change": 159.1144033358181
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 120,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2109.5691323280334
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.0,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
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
