---
timestamp: 1767356250.6359549
datetime: '2026-01-02T07:17:30.635955'
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
  anomaly_id: avg_response_time_1min_1767356250.6359549
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 327.8954081368028
    baseline_value: 676.503940529092
    deviation: 2.532721045916417
    severity: warning
    percentage_change: -51.53089457537281
  system_state:
    active_requests: 4
    completed_requests_1min: 456
    error_rate_1min: 0.0
    avg_response_time_1min: 327.8954081368028
  metadata: {}
  efficiency:
    requests_per_second: 7.6
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 327.90
- **Baseline Value**: 676.50
- **Deviation**: 2.53 standard deviations
- **Change**: -51.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 456
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 327.90ms

### Efficiency Metrics

- **Requests/sec**: 7.60
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 327.8954081368028,
    "baseline_value": 676.503940529092,
    "deviation": 2.532721045916417,
    "severity": "warning",
    "percentage_change": -51.53089457537281
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 456,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 327.8954081368028
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.6,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
