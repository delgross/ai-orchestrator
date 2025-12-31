---
timestamp: 1767168666.9120178
datetime: '2025-12-31T03:11:06.912018'
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
  anomaly_id: avg_response_time_1min_1767168666.9120178
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 112.73117860158284
    baseline_value: 99.9793224647397
    deviation: 1.578030599280309
    severity: warning
    percentage_change: 12.754493451723897
  system_state:
    active_requests: 0
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 112.73117860158284
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 112.73
- **Baseline Value**: 99.98
- **Deviation**: 1.58 standard deviations
- **Change**: +12.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 112.73ms

### Efficiency Metrics

- **Requests/sec**: 0.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 112.73117860158284,
    "baseline_value": 99.9793224647397,
    "deviation": 1.578030599280309,
    "severity": "warning",
    "percentage_change": 12.754493451723897
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 112.73117860158284
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
