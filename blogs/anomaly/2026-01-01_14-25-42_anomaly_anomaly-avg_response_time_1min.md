---
timestamp: 1767295542.200875
datetime: '2026-01-01T14:25:42.200875'
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
  anomaly_id: avg_response_time_1min_1767295542.200875
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 694.775636938922
    baseline_value: 581.842723155888
    deviation: 1.798637216850251
    severity: warning
    percentage_change: 19.409525854425244
  system_state:
    active_requests: 8
    completed_requests_1min: 918
    error_rate_1min: 0.0
    avg_response_time_1min: 694.775636938922
  metadata: {}
  efficiency:
    requests_per_second: 15.3
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 694.78
- **Baseline Value**: 581.84
- **Deviation**: 1.80 standard deviations
- **Change**: +19.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 918
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 694.78ms

### Efficiency Metrics

- **Requests/sec**: 15.30
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 694.775636938922,
    "baseline_value": 581.842723155888,
    "deviation": 1.798637216850251,
    "severity": "warning",
    "percentage_change": 19.409525854425244
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 918,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 694.775636938922
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 15.3,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
