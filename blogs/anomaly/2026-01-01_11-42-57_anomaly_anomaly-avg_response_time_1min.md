---
timestamp: 1767285777.068904
datetime: '2026-01-01T11:42:57.068904'
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
  anomaly_id: avg_response_time_1min_1767285777.068904
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2762.5138221248503
    baseline_value: 785.3401607396652
    deviation: 3.1016443889892447
    severity: critical
    percentage_change: 251.76016205805684
  system_state:
    active_requests: 3
    completed_requests_1min: 93
    error_rate_1min: 0.0
    avg_response_time_1min: 2762.5138221248503
  metadata: {}
  efficiency:
    requests_per_second: 1.55
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2762.51
- **Baseline Value**: 785.34
- **Deviation**: 3.10 standard deviations
- **Change**: +251.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 93
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2762.51ms

### Efficiency Metrics

- **Requests/sec**: 1.55
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
    "current_value": 2762.5138221248503,
    "baseline_value": 785.3401607396652,
    "deviation": 3.1016443889892447,
    "severity": "critical",
    "percentage_change": 251.76016205805684
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 93,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2762.5138221248503
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.55,
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
