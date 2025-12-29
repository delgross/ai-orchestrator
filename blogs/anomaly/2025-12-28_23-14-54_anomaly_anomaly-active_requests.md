---
timestamp: 1766981694.2557461
datetime: '2025-12-28T23:14:54.255746'
category: anomaly
severity: warning
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: active_requests_1766981694.2557461
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 2.0
    baseline_value: 1.009
    deviation: 5.45925124279514
    severity: warning
    percentage_change: 98.21605550049556
  system_state:
    active_requests: 2
    completed_requests_1min: 96
    error_rate_1min: 0.0
    avg_response_time_1min: 178.44144999980927
  metadata: {}
  efficiency:
    requests_per_second: 1.6
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 2.00
- **Baseline Value**: 1.01
- **Deviation**: 5.46 standard deviations
- **Change**: +98.2%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 96
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 178.44ms

### Efficiency Metrics

- **Requests/sec**: 1.60
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 2.0,
    "baseline_value": 1.009,
    "deviation": 5.45925124279514,
    "severity": "warning",
    "percentage_change": 98.21605550049556
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 96,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 178.44144999980927
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
