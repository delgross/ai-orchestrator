---
timestamp: 1767224684.794688
datetime: '2025-12-31T18:44:44.794688'
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
  anomaly_id: avg_response_time_1min_1767224684.794688
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 430.8837254842122
    baseline_value: 305.2489757537842
    deviation: 1.6631398326393287
    severity: warning
    percentage_change: 41.158123273037894
  system_state:
    active_requests: 0
    completed_requests_1min: 3
    error_rate_1min: 0.0
    avg_response_time_1min: 430.8837254842122
  metadata: {}
  efficiency:
    requests_per_second: 0.05
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 430.88
- **Baseline Value**: 305.25
- **Deviation**: 1.66 standard deviations
- **Change**: +41.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 3
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 430.88ms

### Efficiency Metrics

- **Requests/sec**: 0.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 430.8837254842122,
    "baseline_value": 305.2489757537842,
    "deviation": 1.6631398326393287,
    "severity": "warning",
    "percentage_change": 41.158123273037894
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 3,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 430.8837254842122
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
