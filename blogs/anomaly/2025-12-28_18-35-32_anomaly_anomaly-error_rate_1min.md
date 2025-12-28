---
timestamp: 1766964932.805035
datetime: '2025-12-28T18:35:32.805035'
category: anomaly
severity: critical
title: 'Anomaly: error_rate_1min'
source: anomaly_detector
tags:
- anomaly
- error_rate_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: error_rate_1min_1766964932.805035
structured_data:
  anomaly:
    metric_name: error_rate_1min
    current_value: 0.024390243902439025
    baseline_value: 0.0001546072974644403
    deviation: 12.65238962224106
    severity: critical
    percentage_change: 15675.609756097563
  system_state:
    active_requests: 0
    completed_requests_1min: 82
    error_rate_1min: 0.024390243902439025
    avg_response_time_1min: 148.52952084890225
  metadata: {}
  efficiency:
    requests_per_second: 1.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: error_rate_1min

An anomaly was detected in the **error_rate_1min** metric.

## Details

- **Current Value**: 0.02
- **Baseline Value**: 0.00
- **Deviation**: 12.65 standard deviations
- **Change**: +15675.6%
- **Severity**: CRITICAL

**What this means**: Error rate over the last minute. High values indicate system reliability issues.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 82
- **Error Rate (1min)**: 2.44%
- **Avg Response Time (1min)**: 148.53ms

### Efficiency Metrics

- **Requests/sec**: 1.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "error_rate_1min",
    "current_value": 0.024390243902439025,
    "baseline_value": 0.0001546072974644403,
    "deviation": 12.65238962224106,
    "severity": "critical",
    "percentage_change": 15675.609756097563
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 82,
    "error_rate_1min": 0.024390243902439025,
    "avg_response_time_1min": 148.52952084890225
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
