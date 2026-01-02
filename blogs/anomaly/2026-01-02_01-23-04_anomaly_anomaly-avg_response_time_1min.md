---
timestamp: 1767334984.063172
datetime: '2026-01-02T01:23:04.063172'
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
  anomaly_id: avg_response_time_1min_1767334984.063172
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 366.16841952006024
    baseline_value: 816.3235187530518
    deviation: 1.6787239348227643
    severity: warning
    percentage_change: -55.144203112095944
  system_state:
    active_requests: 1
    completed_requests_1min: 12
    error_rate_1min: 0.0
    avg_response_time_1min: 366.16841952006024
  metadata: {}
  efficiency:
    requests_per_second: 0.2
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 366.17
- **Baseline Value**: 816.32
- **Deviation**: 1.68 standard deviations
- **Change**: -55.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 12
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 366.17ms

### Efficiency Metrics

- **Requests/sec**: 0.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 366.16841952006024,
    "baseline_value": 816.3235187530518,
    "deviation": 1.6787239348227643,
    "severity": "warning",
    "percentage_change": -55.144203112095944
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 12,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 366.16841952006024
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
