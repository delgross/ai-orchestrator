---
timestamp: 1767437907.549154
datetime: '2026-01-03T05:58:27.549154'
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
  anomaly_id: avg_response_time_1min_1767437907.549154
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 547.5264449091353
    baseline_value: 531.1297107730392
    deviation: 2.752332045147608
    severity: warning
    percentage_change: 3.0871430845454526
  system_state:
    active_requests: 6
    completed_requests_1min: 676
    error_rate_1min: 0.0
    avg_response_time_1min: 547.5264449091353
  metadata: {}
  efficiency:
    requests_per_second: 11.266666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 547.53
- **Baseline Value**: 531.13
- **Deviation**: 2.75 standard deviations
- **Change**: +3.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 676
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 547.53ms

### Efficiency Metrics

- **Requests/sec**: 11.27
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 547.5264449091353,
    "baseline_value": 531.1297107730392,
    "deviation": 2.752332045147608,
    "severity": "warning",
    "percentage_change": 3.0871430845454526
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 676,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 547.5264449091353
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.266666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
