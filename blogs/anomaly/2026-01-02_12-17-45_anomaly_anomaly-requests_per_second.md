---
timestamp: 1767374265.321751
datetime: '2026-01-02T12:17:45.321751'
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
  anomaly_id: requests_per_second_1767374265.321751
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.95
    baseline_value: 13.183333333333334
    deviation: 4.60000000000001
    severity: critical
    percentage_change: 5.815423514538551
  system_state:
    active_requests: 9
    completed_requests_1min: 837
    error_rate_1min: 0.0
    avg_response_time_1min: 522.785250858594
  metadata: {}
  efficiency:
    requests_per_second: 13.95
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.95
- **Baseline Value**: 13.18
- **Deviation**: 4.60 standard deviations
- **Change**: +5.8%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 837
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 522.79ms

### Efficiency Metrics

- **Requests/sec**: 13.95
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.95,
    "baseline_value": 13.183333333333334,
    "deviation": 4.60000000000001,
    "severity": "critical",
    "percentage_change": 5.815423514538551
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 837,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 522.785250858594
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.95,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
