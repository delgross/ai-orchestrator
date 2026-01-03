---
timestamp: 1767450330.241801
datetime: '2026-01-03T09:25:30.241801'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767450330.241801
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 588.6455020685305
    baseline_value: 547.5185997497135
    deviation: 2.408463587475927
    severity: warning
    percentage_change: 7.511507798569266
  system_state:
    active_requests: 0
    completed_requests_1min: 87
    error_rate_1min: 0.0
    avg_response_time_1min: 588.6455020685305
  metadata: {}
  efficiency:
    requests_per_second: 1.45
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 588.65
- **Baseline Value**: 547.52
- **Deviation**: 2.41 standard deviations
- **Change**: +7.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 87
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 588.65ms

### Efficiency Metrics

- **Requests/sec**: 1.45
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 588.6455020685305,
    "baseline_value": 547.5185997497135,
    "deviation": 2.408463587475927,
    "severity": "warning",
    "percentage_change": 7.511507798569266
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 87,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 588.6455020685305
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.45,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
