---
timestamp: 1766886065.4529028
datetime: '2025-12-27T20:41:05.452903'
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
  anomaly_id: avg_response_time_1min_1766886065.4529028
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 22.269773483276367
    baseline_value: 138.1027579499571
    deviation: 4.652095877008263
    severity: warning
    percentage_change: -83.87449040565429
  system_state:
    active_requests: 1
    completed_requests_1min: 60
    error_rate_1min: 0.0
    avg_response_time_1min: 22.269773483276367
  metadata: {}
  efficiency:
    requests_per_second: 1.0
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 22.27
- **Baseline Value**: 138.10
- **Deviation**: 4.65 standard deviations
- **Change**: -83.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 60
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 22.27ms

### Efficiency Metrics

- **Requests/sec**: 1.00
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 22.269773483276367,
    "baseline_value": 138.1027579499571,
    "deviation": 4.652095877008263,
    "severity": "warning",
    "percentage_change": -83.87449040565429
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 60,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 22.269773483276367
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
