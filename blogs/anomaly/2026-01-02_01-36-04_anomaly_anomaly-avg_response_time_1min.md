---
timestamp: 1767335764.220591
datetime: '2026-01-02T01:36:04.220591'
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
  anomaly_id: avg_response_time_1min_1767335764.220591
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1701.9530236721039
    baseline_value: 1111.2354755401611
    deviation: 2.003030174047399
    severity: warning
    percentage_change: 53.1586293935406
  system_state:
    active_requests: 1
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 1701.9530236721039
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1701.95
- **Baseline Value**: 1111.24
- **Deviation**: 2.00 standard deviations
- **Change**: +53.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1701.95ms

### Efficiency Metrics

- **Requests/sec**: 0.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1701.9530236721039,
    "baseline_value": 1111.2354755401611,
    "deviation": 2.003030174047399,
    "severity": "warning",
    "percentage_change": 53.1586293935406
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1701.9530236721039
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
