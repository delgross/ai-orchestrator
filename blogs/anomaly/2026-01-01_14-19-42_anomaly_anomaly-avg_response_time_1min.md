---
timestamp: 1767295182.154939
datetime: '2026-01-01T14:19:42.154939'
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
  anomaly_id: avg_response_time_1min_1767295182.154939
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 667.5291606689601
    baseline_value: 513.533968873204
    deviation: 2.4125405608471797
    severity: warning
    percentage_change: 29.987342830242035
  system_state:
    active_requests: 7
    completed_requests_1min: 822
    error_rate_1min: 0.0
    avg_response_time_1min: 667.5291606689601
  metadata: {}
  efficiency:
    requests_per_second: 13.7
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 667.53
- **Baseline Value**: 513.53
- **Deviation**: 2.41 standard deviations
- **Change**: +30.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 822
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 667.53ms

### Efficiency Metrics

- **Requests/sec**: 13.70
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 667.5291606689601,
    "baseline_value": 513.533968873204,
    "deviation": 2.4125405608471797,
    "severity": "warning",
    "percentage_change": 29.987342830242035
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 822,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 667.5291606689601
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.7,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
