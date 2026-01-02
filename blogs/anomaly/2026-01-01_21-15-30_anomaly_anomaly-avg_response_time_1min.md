---
timestamp: 1767320130.677917
datetime: '2026-01-01T21:15:30.677917'
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
  anomaly_id: avg_response_time_1min_1767320130.677917
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 533.9687710159395
    baseline_value: 509.76214791736464
    deviation: 1.6421139078017086
    severity: warning
    percentage_change: 4.7486113273555395
  system_state:
    active_requests: 7
    completed_requests_1min: 815
    error_rate_1min: 0.0
    avg_response_time_1min: 533.9687710159395
  metadata: {}
  efficiency:
    requests_per_second: 13.583333333333334
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 533.97
- **Baseline Value**: 509.76
- **Deviation**: 1.64 standard deviations
- **Change**: +4.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 815
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 533.97ms

### Efficiency Metrics

- **Requests/sec**: 13.58
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 533.9687710159395,
    "baseline_value": 509.76214791736464,
    "deviation": 1.6421139078017086,
    "severity": "warning",
    "percentage_change": 4.7486113273555395
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 815,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 533.9687710159395
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.583333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
