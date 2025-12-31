---
timestamp: 1767154024.610562
datetime: '2025-12-30T23:07:04.610562'
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
  anomaly_id: avg_response_time_1min_1767154024.610562
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 107.20220550161893
    baseline_value: 91.92348503675618
    deviation: 1.9713190275725354
    severity: warning
    percentage_change: 16.6211283860196
  system_state:
    active_requests: 0
    completed_requests_1min: 122
    error_rate_1min: 0.0
    avg_response_time_1min: 107.20220550161893
  metadata: {}
  efficiency:
    requests_per_second: 2.033333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 107.20
- **Baseline Value**: 91.92
- **Deviation**: 1.97 standard deviations
- **Change**: +16.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 122
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 107.20ms

### Efficiency Metrics

- **Requests/sec**: 2.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 107.20220550161893,
    "baseline_value": 91.92348503675618,
    "deviation": 1.9713190275725354,
    "severity": "warning",
    "percentage_change": 16.6211283860196
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 122,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 107.20220550161893
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.033333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
