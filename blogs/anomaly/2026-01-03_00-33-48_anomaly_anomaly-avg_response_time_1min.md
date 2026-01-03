---
timestamp: 1767418428.492602
datetime: '2026-01-03T00:33:48.492602'
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
  anomaly_id: avg_response_time_1min_1767418428.492602
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 758.6240314967339
    baseline_value: 877.0503930526205
    deviation: 2.086459405447798
    severity: warning
    percentage_change: -13.502800123456687
  system_state:
    active_requests: 25
    completed_requests_1min: 1877
    error_rate_1min: 0.0
    avg_response_time_1min: 758.6240314967339
  metadata: {}
  efficiency:
    requests_per_second: 31.283333333333335
    cache_hit_rate: 0.0
    queue_depth: 25
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 758.62
- **Baseline Value**: 877.05
- **Deviation**: 2.09 standard deviations
- **Change**: -13.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 25
- **Completed Requests (1min)**: 1877
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 758.62ms

### Efficiency Metrics

- **Requests/sec**: 31.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 25

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 758.6240314967339,
    "baseline_value": 877.0503930526205,
    "deviation": 2.086459405447798,
    "severity": "warning",
    "percentage_change": -13.502800123456687
  },
  "system_state": {
    "active_requests": 25,
    "completed_requests_1min": 1877,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 758.6240314967339
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 31.283333333333335,
    "cache_hit_rate": 0.0,
    "queue_depth": 25
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
