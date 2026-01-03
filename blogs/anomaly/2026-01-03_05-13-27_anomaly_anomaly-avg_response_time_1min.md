---
timestamp: 1767435207.0173252
datetime: '2026-01-03T05:13:27.017325'
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
  anomaly_id: avg_response_time_1min_1767435207.0173252
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 522.4495603797141
    baseline_value: 535.9400537357642
    deviation: 1.6413262760967928
    severity: warning
    percentage_change: -2.5171646086189683
  system_state:
    active_requests: 6
    completed_requests_1min: 712
    error_rate_1min: 0.0
    avg_response_time_1min: 522.4495603797141
  metadata: {}
  efficiency:
    requests_per_second: 11.866666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 522.45
- **Baseline Value**: 535.94
- **Deviation**: 1.64 standard deviations
- **Change**: -2.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 712
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 522.45ms

### Efficiency Metrics

- **Requests/sec**: 11.87
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 522.4495603797141,
    "baseline_value": 535.9400537357642,
    "deviation": 1.6413262760967928,
    "severity": "warning",
    "percentage_change": -2.5171646086189683
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 712,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 522.4495603797141
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.866666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
