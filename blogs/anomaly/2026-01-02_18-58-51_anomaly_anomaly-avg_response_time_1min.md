---
timestamp: 1767398331.258369
datetime: '2026-01-02T18:58:51.258369'
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
  anomaly_id: avg_response_time_1min_1767398331.258369
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 427.22072122303865
    baseline_value: 405.4621109241841
    deviation: 1.6904947069837222
    severity: warning
    percentage_change: 5.366373259700978
  system_state:
    active_requests: 3
    completed_requests_1min: 438
    error_rate_1min: 0.0
    avg_response_time_1min: 427.22072122303865
  metadata: {}
  efficiency:
    requests_per_second: 7.3
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 427.22
- **Baseline Value**: 405.46
- **Deviation**: 1.69 standard deviations
- **Change**: +5.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 438
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 427.22ms

### Efficiency Metrics

- **Requests/sec**: 7.30
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 427.22072122303865,
    "baseline_value": 405.4621109241841,
    "deviation": 1.6904947069837222,
    "severity": "warning",
    "percentage_change": 5.366373259700978
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 438,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 427.22072122303865
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.3,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
