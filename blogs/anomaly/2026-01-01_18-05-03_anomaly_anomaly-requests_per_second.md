---
timestamp: 1767308703.3517509
datetime: '2026-01-01T18:05:03.351751'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1767308703.3517509
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.716666666666667
    baseline_value: 2.25
    deviation: 2.977777777777778
    severity: warning
    percentage_change: 198.5185185185185
  system_state:
    active_requests: 2
    completed_requests_1min: 403
    error_rate_1min: 0.0
    avg_response_time_1min: 250.84124723675825
  metadata: {}
  efficiency:
    requests_per_second: 6.716666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.72
- **Baseline Value**: 2.25
- **Deviation**: 2.98 standard deviations
- **Change**: +198.5%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 403
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 250.84ms

### Efficiency Metrics

- **Requests/sec**: 6.72
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.716666666666667,
    "baseline_value": 2.25,
    "deviation": 2.977777777777778,
    "severity": "warning",
    "percentage_change": 198.5185185185185
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 403,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 250.84124723675825
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.716666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
