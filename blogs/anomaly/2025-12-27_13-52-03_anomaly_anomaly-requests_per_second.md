---
timestamp: 1766861523.853544
datetime: '2025-12-27T13:52:03.853544'
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
  anomaly_id: requests_per_second_1766861523.853544
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 3.0166666666666666
    baseline_value: 2.43975
    deviation: 6.610902862978905
    severity: critical
    percentage_change: 23.64654848515899
  system_state:
    active_requests: 1
    completed_requests_1min: 181
    error_rate_1min: 0.0
    avg_response_time_1min: 363.7890249326084
  metadata: {}
  efficiency:
    requests_per_second: 3.0166666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 3.02
- **Baseline Value**: 2.44
- **Deviation**: 6.61 standard deviations
- **Change**: +23.6%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 181
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 363.79ms

### Efficiency Metrics

- **Requests/sec**: 3.02
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
    "current_value": 3.0166666666666666,
    "baseline_value": 2.43975,
    "deviation": 6.610902862978905,
    "severity": "critical",
    "percentage_change": 23.64654848515899
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 181,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 363.7890249326084
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.0166666666666666,
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
