---
timestamp: 1766955437.7361972
datetime: '2025-12-28T15:57:17.736197'
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
  anomaly_id: requests_per_second_1766955437.7361972
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.75
    baseline_value: 0.044257703081232495
    deviation: 10.561343415460277
    severity: critical
    percentage_change: 1594.620253164557
  system_state:
    active_requests: 1
    completed_requests_1min: 45
    error_rate_1min: 0.0
    avg_response_time_1min: 222.72184689839682
  metadata: {}
  efficiency:
    requests_per_second: 0.75
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.75
- **Baseline Value**: 0.04
- **Deviation**: 10.56 standard deviations
- **Change**: +1594.6%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 45
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 222.72ms

### Efficiency Metrics

- **Requests/sec**: 0.75
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
    "current_value": 0.75,
    "baseline_value": 0.044257703081232495,
    "deviation": 10.561343415460277,
    "severity": "critical",
    "percentage_change": 1594.620253164557
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 45,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 222.72184689839682
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.75,
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
