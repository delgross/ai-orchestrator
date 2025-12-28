---
timestamp: 1766850799.5734951
datetime: '2025-12-27T10:53:19.573495'
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
  anomaly_id: requests_per_second_1766850799.5734951
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 2.3666666666666667
    baseline_value: 0.9450904392764857
    deviation: 11.636668717884787
    severity: critical
    percentage_change: 150.41695146958304
  system_state:
    active_requests: 104
    completed_requests_1min: 142
    error_rate_1min: 0.0
    avg_response_time_1min: 683.9418444834964
  metadata: {}
  efficiency:
    requests_per_second: 2.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 104
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 2.37
- **Baseline Value**: 0.95
- **Deviation**: 11.64 standard deviations
- **Change**: +150.4%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 104
- **Completed Requests (1min)**: 142
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 683.94ms

### Efficiency Metrics

- **Requests/sec**: 2.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 104

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 2.3666666666666667,
    "baseline_value": 0.9450904392764857,
    "deviation": 11.636668717884787,
    "severity": "critical",
    "percentage_change": 150.41695146958304
  },
  "system_state": {
    "active_requests": 104,
    "completed_requests_1min": 142,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 683.9418444834964
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.3666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 104
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
