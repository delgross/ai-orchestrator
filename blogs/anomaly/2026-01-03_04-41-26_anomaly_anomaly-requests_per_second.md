---
timestamp: 1767433286.644147
datetime: '2026-01-03T04:41:26.644147'
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
  anomaly_id: requests_per_second_1767433286.644147
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.25
    baseline_value: 11.633333333333333
    deviation: 3.8333333333333424
    severity: critical
    percentage_change: -3.2951289398280763
  system_state:
    active_requests: 6
    completed_requests_1min: 675
    error_rate_1min: 0.0
    avg_response_time_1min: 528.421349702058
  metadata: {}
  efficiency:
    requests_per_second: 11.25
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.25
- **Baseline Value**: 11.63
- **Deviation**: 3.83 standard deviations
- **Change**: -3.3%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 675
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 528.42ms

### Efficiency Metrics

- **Requests/sec**: 11.25
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
    "current_value": 11.25,
    "baseline_value": 11.633333333333333,
    "deviation": 3.8333333333333424,
    "severity": "critical",
    "percentage_change": -3.2951289398280763
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 675,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 528.421349702058
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.25,
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
