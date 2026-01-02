---
timestamp: 1767341284.9021251
datetime: '2026-01-02T03:08:04.902125'
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
  anomaly_id: requests_per_second_1767341284.9021251
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.95
    baseline_value: 14.066666666666666
    deviation: 1.7500000000000133
    severity: warning
    percentage_change: -0.8293838862559275
  system_state:
    active_requests: 6
    completed_requests_1min: 837
    error_rate_1min: 0.0
    avg_response_time_1min: 433.06524494358
  metadata: {}
  efficiency:
    requests_per_second: 13.95
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.95
- **Baseline Value**: 14.07
- **Deviation**: 1.75 standard deviations
- **Change**: -0.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 837
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 433.07ms

### Efficiency Metrics

- **Requests/sec**: 13.95
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.95,
    "baseline_value": 14.066666666666666,
    "deviation": 1.7500000000000133,
    "severity": "warning",
    "percentage_change": -0.8293838862559275
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 837,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 433.06524494358
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.95,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
