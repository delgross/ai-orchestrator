---
timestamp: 1767018862.719244
datetime: '2025-12-29T09:34:22.719244'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767018862.719244
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.85
    baseline_value: 3.0315686274509805
    deviation: 6.209902479758469
    severity: critical
    percentage_change: 92.96940689476746
  system_state:
    active_requests: 1
    completed_requests_1min: 351
    error_rate_1min: 0.0
    avg_response_time_1min: 140.99900471179234
  metadata: {}
  efficiency:
    requests_per_second: 5.85
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.85
- **Baseline Value**: 3.03
- **Deviation**: 6.21 standard deviations
- **Change**: +93.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 351
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 141.00ms

### Efficiency Metrics

- **Requests/sec**: 5.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.85,
    "baseline_value": 3.0315686274509805,
    "deviation": 6.209902479758469,
    "severity": "critical",
    "percentage_change": 92.96940689476746
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 351,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 140.99900471179234
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
