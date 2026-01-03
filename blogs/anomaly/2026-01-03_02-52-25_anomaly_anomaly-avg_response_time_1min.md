---
timestamp: 1767426745.165034
datetime: '2026-01-03T02:52:25.165034'
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
  anomaly_id: avg_response_time_1min_1767426745.165034
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 593.3269972016891
    baseline_value: 557.0700042931609
    deviation: 2.06041196044795
    severity: warning
    percentage_change: 6.5085164573764756
  system_state:
    active_requests: 7
    completed_requests_1min: 687
    error_rate_1min: 0.0
    avg_response_time_1min: 593.3269972016891
  metadata: {}
  efficiency:
    requests_per_second: 11.45
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 593.33
- **Baseline Value**: 557.07
- **Deviation**: 2.06 standard deviations
- **Change**: +6.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 687
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 593.33ms

### Efficiency Metrics

- **Requests/sec**: 11.45
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 593.3269972016891,
    "baseline_value": 557.0700042931609,
    "deviation": 2.06041196044795,
    "severity": "warning",
    "percentage_change": 6.5085164573764756
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 687,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 593.3269972016891
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.45,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
