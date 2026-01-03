---
timestamp: 1767378617.9958348
datetime: '2026-01-02T13:30:17.995835'
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
  anomaly_id: avg_response_time_1min_1767378617.9958348
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1007.479118856978
    baseline_value: 678.6212080221037
    deviation: 1.629813615951973
    severity: warning
    percentage_change: 48.45971610485873
  system_state:
    active_requests: 9
    completed_requests_1min: 752
    error_rate_1min: 0.0
    avg_response_time_1min: 1007.479118856978
  metadata: {}
  efficiency:
    requests_per_second: 12.533333333333333
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1007.48
- **Baseline Value**: 678.62
- **Deviation**: 1.63 standard deviations
- **Change**: +48.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 752
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1007.48ms

### Efficiency Metrics

- **Requests/sec**: 12.53
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1007.479118856978,
    "baseline_value": 678.6212080221037,
    "deviation": 1.629813615951973,
    "severity": "warning",
    "percentage_change": 48.45971610485873
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 752,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1007.479118856978
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.533333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
