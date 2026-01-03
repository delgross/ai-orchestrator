---
timestamp: 1767448349.778594
datetime: '2026-01-03T08:52:29.778594'
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
  anomaly_id: requests_per_second_1767448349.778594
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.25
    baseline_value: 11.45
    deviation: 1.7142857142857013
    severity: warning
    percentage_change: -1.7467248908296884
  system_state:
    active_requests: 6
    completed_requests_1min: 675
    error_rate_1min: 0.0
    avg_response_time_1min: 530.6525233939842
  metadata: {}
  efficiency:
    requests_per_second: 11.25
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.25
- **Baseline Value**: 11.45
- **Deviation**: 1.71 standard deviations
- **Change**: -1.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 675
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 530.65ms

### Efficiency Metrics

- **Requests/sec**: 11.25
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.25,
    "baseline_value": 11.45,
    "deviation": 1.7142857142857013,
    "severity": "warning",
    "percentage_change": -1.7467248908296884
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 675,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 530.6525233939842
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.25,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
