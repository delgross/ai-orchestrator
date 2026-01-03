---
timestamp: 1767379394.367289
datetime: '2026-01-02T13:43:14.367289'
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
  anomaly_id: avg_response_time_1min_1767379394.367289
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 559.7573165166176
    baseline_value: 482.1894786272391
    deviation: 1.9209999781798581
    severity: warning
    percentage_change: 16.086588639430477
  system_state:
    active_requests: 8
    completed_requests_1min: 708
    error_rate_1min: 0.0
    avg_response_time_1min: 559.7573165166176
  metadata: {}
  efficiency:
    requests_per_second: 11.8
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 559.76
- **Baseline Value**: 482.19
- **Deviation**: 1.92 standard deviations
- **Change**: +16.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 708
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 559.76ms

### Efficiency Metrics

- **Requests/sec**: 11.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 559.7573165166176,
    "baseline_value": 482.1894786272391,
    "deviation": 1.9209999781798581,
    "severity": "warning",
    "percentage_change": 16.086588639430477
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 708,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 559.7573165166176
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
