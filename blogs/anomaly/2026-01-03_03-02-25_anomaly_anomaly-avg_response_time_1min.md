---
timestamp: 1767427345.3750222
datetime: '2026-01-03T03:02:25.375022'
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
  anomaly_id: avg_response_time_1min_1767427345.3750222
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 547.7243273598807
    baseline_value: 535.1280875738848
    deviation: 1.7125394724007916
    severity: warning
    percentage_change: 2.3538737880688623
  system_state:
    active_requests: 6
    completed_requests_1min: 700
    error_rate_1min: 0.0
    avg_response_time_1min: 547.7243273598807
  metadata: {}
  efficiency:
    requests_per_second: 11.666666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 547.72
- **Baseline Value**: 535.13
- **Deviation**: 1.71 standard deviations
- **Change**: +2.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 700
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 547.72ms

### Efficiency Metrics

- **Requests/sec**: 11.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 547.7243273598807,
    "baseline_value": 535.1280875738848,
    "deviation": 1.7125394724007916,
    "severity": "warning",
    "percentage_change": 2.3538737880688623
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 700,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 547.7243273598807
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
