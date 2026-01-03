---
timestamp: 1767458974.937139
datetime: '2026-01-03T11:49:34.937139'
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
  anomaly_id: avg_response_time_1min_1767458974.937139
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 898.9956038338797
    baseline_value: 557.1566444115351
    deviation: 1.5221876743753282
    severity: warning
    percentage_change: 61.354192371409745
  system_state:
    active_requests: 0
    completed_requests_1min: 7
    error_rate_1min: 0.0
    avg_response_time_1min: 898.9956038338797
  metadata: {}
  efficiency:
    requests_per_second: 0.11666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 899.00
- **Baseline Value**: 557.16
- **Deviation**: 1.52 standard deviations
- **Change**: +61.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 7
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 899.00ms

### Efficiency Metrics

- **Requests/sec**: 0.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 898.9956038338797,
    "baseline_value": 557.1566444115351,
    "deviation": 1.5221876743753282,
    "severity": "warning",
    "percentage_change": 61.354192371409745
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 7,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 898.9956038338797
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.11666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
