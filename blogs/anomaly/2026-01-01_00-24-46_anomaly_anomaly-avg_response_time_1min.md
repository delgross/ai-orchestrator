---
timestamp: 1767245086.3552551
datetime: '2026-01-01T00:24:46.355255'
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
  anomaly_id: avg_response_time_1min_1767245086.3552551
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 231.10138873259226
    baseline_value: 181.43616953203755
    deviation: 2.41635800234415
    severity: warning
    percentage_change: 27.37338388958048
  system_state:
    active_requests: 0
    completed_requests_1min: 48
    error_rate_1min: 0.0
    avg_response_time_1min: 231.10138873259226
  metadata: {}
  efficiency:
    requests_per_second: 0.8
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 231.10
- **Baseline Value**: 181.44
- **Deviation**: 2.42 standard deviations
- **Change**: +27.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 48
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 231.10ms

### Efficiency Metrics

- **Requests/sec**: 0.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 231.10138873259226,
    "baseline_value": 181.43616953203755,
    "deviation": 2.41635800234415,
    "severity": "warning",
    "percentage_change": 27.37338388958048
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 48,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 231.10138873259226
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
