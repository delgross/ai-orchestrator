---
timestamp: 1767437067.438626
datetime: '2026-01-03T05:44:27.438626'
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
  anomaly_id: requests_per_second_1767437067.438626
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.483333333333333
    baseline_value: 11.85
    deviation: 4.399999999999975
    severity: critical
    percentage_change: -3.0942334739803132
  system_state:
    active_requests: 6
    completed_requests_1min: 689
    error_rate_1min: 0.0
    avg_response_time_1min: 529.7200361426233
  metadata: {}
  efficiency:
    requests_per_second: 11.483333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.48
- **Baseline Value**: 11.85
- **Deviation**: 4.40 standard deviations
- **Change**: -3.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 689
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 529.72ms

### Efficiency Metrics

- **Requests/sec**: 11.48
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.483333333333333,
    "baseline_value": 11.85,
    "deviation": 4.399999999999975,
    "severity": "critical",
    "percentage_change": -3.0942334739803132
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 689,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 529.7200361426233
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.483333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
