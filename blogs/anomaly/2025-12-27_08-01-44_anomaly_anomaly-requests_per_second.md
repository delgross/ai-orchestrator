---
timestamp: 1766840504.6648152
datetime: '2025-12-27T08:01:44.664815'
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
  anomaly_id: requests_per_second_1766840504.6648152
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.35
    baseline_value: 0.12016666666666667
    deviation: 6.249802318513635
    severity: critical
    percentage_change: 1023.4396671289876
  system_state:
    active_requests: 0
    completed_requests_1min: 81
    error_rate_1min: 0.0
    avg_response_time_1min: 18.932872348361546
  metadata: {}
  efficiency:
    requests_per_second: 1.35
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.35
- **Baseline Value**: 0.12
- **Deviation**: 6.25 standard deviations
- **Change**: +1023.4%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 81
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 18.93ms

### Efficiency Metrics

- **Requests/sec**: 1.35
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.35,
    "baseline_value": 0.12016666666666667,
    "deviation": 6.249802318513635,
    "severity": "critical",
    "percentage_change": 1023.4396671289876
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 81,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 18.932872348361546
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.35,
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
