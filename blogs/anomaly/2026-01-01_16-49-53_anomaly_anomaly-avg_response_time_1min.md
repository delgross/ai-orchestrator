---
timestamp: 1767304193.66541
datetime: '2026-01-01T16:49:53.665410'
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
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767304193.66541
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 867.0215554097119
    baseline_value: 463.5757236480713
    deviation: 3.8011562201682785
    severity: critical
    percentage_change: 87.02911114213589
  system_state:
    active_requests: 2
    completed_requests_1min: 136
    error_rate_1min: 0.0
    avg_response_time_1min: 867.0215554097119
  metadata: {}
  efficiency:
    requests_per_second: 2.2666666666666666
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 867.02
- **Baseline Value**: 463.58
- **Deviation**: 3.80 standard deviations
- **Change**: +87.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 136
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 867.02ms

### Efficiency Metrics

- **Requests/sec**: 2.27
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 867.0215554097119,
    "baseline_value": 463.5757236480713,
    "deviation": 3.8011562201682785,
    "severity": "critical",
    "percentage_change": 87.02911114213589
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 136,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 867.0215554097119
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.2666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
