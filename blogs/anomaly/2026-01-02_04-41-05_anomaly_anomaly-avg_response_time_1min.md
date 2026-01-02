---
timestamp: 1767346865.701521
datetime: '2026-01-02T04:41:05.701521'
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
  anomaly_id: avg_response_time_1min_1767346865.701521
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 440.9617130617494
    baseline_value: 436.32774685437863
    deviation: 2.2275089023300363
    severity: warning
    percentage_change: 1.0620379384025975
  system_state:
    active_requests: 6
    completed_requests_1min: 824
    error_rate_1min: 0.0
    avg_response_time_1min: 440.9617130617494
  metadata: {}
  efficiency:
    requests_per_second: 13.733333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 440.96
- **Baseline Value**: 436.33
- **Deviation**: 2.23 standard deviations
- **Change**: +1.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 824
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 440.96ms

### Efficiency Metrics

- **Requests/sec**: 13.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 440.9617130617494,
    "baseline_value": 436.32774685437863,
    "deviation": 2.2275089023300363,
    "severity": "warning",
    "percentage_change": 1.0620379384025975
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 824,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 440.9617130617494
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.733333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
