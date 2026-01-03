---
timestamp: 1767459095.004662
datetime: '2026-01-03T11:51:35.004662'
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
  anomaly_id: avg_response_time_1min_1767459095.004662
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2422.0343430836997
    baseline_value: 557.8512436634785
    deviation: 8.263705456855076
    severity: critical
    percentage_change: 334.1720791331214
  system_state:
    active_requests: 0
    completed_requests_1min: 18
    error_rate_1min: 0.0
    avg_response_time_1min: 2422.0343430836997
  metadata: {}
  efficiency:
    requests_per_second: 0.3
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2422.03
- **Baseline Value**: 557.85
- **Deviation**: 8.26 standard deviations
- **Change**: +334.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 18
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2422.03ms

### Efficiency Metrics

- **Requests/sec**: 0.30
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
    "current_value": 2422.0343430836997,
    "baseline_value": 557.8512436634785,
    "deviation": 8.263705456855076,
    "severity": "critical",
    "percentage_change": 334.1720791331214
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 18,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2422.0343430836997
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.3,
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
