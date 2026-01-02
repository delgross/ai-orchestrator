---
timestamp: 1767371984.888787
datetime: '2026-01-02T11:39:44.888787'
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
  anomaly_id: avg_response_time_1min_1767371984.888787
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 644.9243662437955
    baseline_value: 774.8950054803657
    deviation: 1.5027985331471954
    severity: warning
    percentage_change: -16.77267737143306
  system_state:
    active_requests: 10
    completed_requests_1min: 828
    error_rate_1min: 0.0
    avg_response_time_1min: 644.9243662437955
  metadata: {}
  efficiency:
    requests_per_second: 13.8
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 644.92
- **Baseline Value**: 774.90
- **Deviation**: 1.50 standard deviations
- **Change**: -16.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 828
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 644.92ms

### Efficiency Metrics

- **Requests/sec**: 13.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 644.9243662437955,
    "baseline_value": 774.8950054803657,
    "deviation": 1.5027985331471954,
    "severity": "warning",
    "percentage_change": -16.77267737143306
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 828,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 644.9243662437955
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
