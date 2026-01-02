---
timestamp: 1767345485.4940732
datetime: '2026-01-02T04:18:05.494073'
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
  anomaly_id: requests_per_second_1767345485.4940732
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.9
    baseline_value: 13.666666666666666
    deviation: 1.5555555555555767
    severity: warning
    percentage_change: 1.7073170731707388
  system_state:
    active_requests: 6
    completed_requests_1min: 834
    error_rate_1min: 0.0
    avg_response_time_1min: 435.7061617666011
  metadata: {}
  efficiency:
    requests_per_second: 13.9
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.90
- **Baseline Value**: 13.67
- **Deviation**: 1.56 standard deviations
- **Change**: +1.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 834
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 435.71ms

### Efficiency Metrics

- **Requests/sec**: 13.90
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.9,
    "baseline_value": 13.666666666666666,
    "deviation": 1.5555555555555767,
    "severity": "warning",
    "percentage_change": 1.7073170731707388
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 834,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 435.7061617666011
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.9,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
