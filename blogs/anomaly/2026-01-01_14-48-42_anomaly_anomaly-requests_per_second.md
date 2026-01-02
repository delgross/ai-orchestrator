---
timestamp: 1767296922.356993
datetime: '2026-01-01T14:48:42.356993'
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
  anomaly_id: requests_per_second_1767296922.356993
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.683333333333334
    baseline_value: 13.8
    deviation: 4.076923076923072
    severity: critical
    percentage_change: 6.400966183574876
  system_state:
    active_requests: 7
    completed_requests_1min: 881
    error_rate_1min: 0.0
    avg_response_time_1min: 515.9530791197137
  metadata: {}
  efficiency:
    requests_per_second: 14.683333333333334
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.68
- **Baseline Value**: 13.80
- **Deviation**: 4.08 standard deviations
- **Change**: +6.4%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 881
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 515.95ms

### Efficiency Metrics

- **Requests/sec**: 14.68
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.683333333333334,
    "baseline_value": 13.8,
    "deviation": 4.076923076923072,
    "severity": "critical",
    "percentage_change": 6.400966183574876
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 881,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 515.9530791197137
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.683333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
