---
timestamp: 1767164466.561263
datetime: '2025-12-31T02:01:06.561263'
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
  anomaly_id: avg_response_time_1min_1767164466.561263
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 123.82058823694948
    baseline_value: 101.13337243250174
    deviation: 2.457354766249302
    severity: warning
    percentage_change: 22.43296674358367
  system_state:
    active_requests: 0
    completed_requests_1min: 122
    error_rate_1min: 0.0
    avg_response_time_1min: 123.82058823694948
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

- **Current Value**: 123.82
- **Baseline Value**: 101.13
- **Deviation**: 2.46 standard deviations
- **Change**: +22.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 122
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 123.82ms

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
    "current_value": 123.82058823694948,
    "baseline_value": 101.13337243250174,
    "deviation": 2.457354766249302,
    "severity": "warning",
    "percentage_change": 22.43296674358367
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 122,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 123.82058823694948
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
