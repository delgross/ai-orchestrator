---
timestamp: 1767299562.625088
datetime: '2026-01-01T15:32:42.625088'
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
  anomaly_id: avg_response_time_1min_1767299562.625088
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5543.45490137736
    baseline_value: 1295.874228519676
    deviation: 5.325704300717585
    severity: critical
    percentage_change: 327.77723172331696
  system_state:
    active_requests: 1
    completed_requests_1min: 15
    error_rate_1min: 0.0
    avg_response_time_1min: 5543.45490137736
  metadata: {}
  efficiency:
    requests_per_second: 0.25
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5543.45
- **Baseline Value**: 1295.87
- **Deviation**: 5.33 standard deviations
- **Change**: +327.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 15
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 5543.45ms

### Efficiency Metrics

- **Requests/sec**: 0.25
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
    "current_value": 5543.45490137736,
    "baseline_value": 1295.874228519676,
    "deviation": 5.325704300717585,
    "severity": "critical",
    "percentage_change": 327.77723172331696
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 15,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 5543.45490137736
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.25,
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
