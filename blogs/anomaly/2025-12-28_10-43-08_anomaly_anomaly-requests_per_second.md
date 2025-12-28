---
timestamp: 1766936588.8413508
datetime: '2025-12-28T10:43:08.841351'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1766936588.8413508
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 2.7333333333333334
    baseline_value: 0.6067333333333333
    deviation: 4.869496848209422
    severity: warning
    percentage_change: 350.49994506098227
  system_state:
    active_requests: 0
    completed_requests_1min: 164
    error_rate_1min: 0.0
    avg_response_time_1min: 99.95134138479466
  metadata: {}
  efficiency:
    requests_per_second: 2.7333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 2.73
- **Baseline Value**: 0.61
- **Deviation**: 4.87 standard deviations
- **Change**: +350.5%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 164
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 99.95ms

### Efficiency Metrics

- **Requests/sec**: 2.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 2.7333333333333334,
    "baseline_value": 0.6067333333333333,
    "deviation": 4.869496848209422,
    "severity": "warning",
    "percentage_change": 350.49994506098227
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 164,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 99.95134138479466
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.7333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
