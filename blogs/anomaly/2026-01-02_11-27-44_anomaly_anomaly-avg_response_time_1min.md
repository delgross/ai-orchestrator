---
timestamp: 1767371264.811836
datetime: '2026-01-02T11:27:44.811836'
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
  anomaly_id: avg_response_time_1min_1767371264.811836
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 590.5800145431604
    baseline_value: 364.12102149592505
    deviation: 1.656736247712116
    severity: warning
    percentage_change: 62.19333124928347
  system_state:
    active_requests: 3
    completed_requests_1min: 179
    error_rate_1min: 0.0
    avg_response_time_1min: 590.5800145431604
  metadata: {}
  efficiency:
    requests_per_second: 2.9833333333333334
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 590.58
- **Baseline Value**: 364.12
- **Deviation**: 1.66 standard deviations
- **Change**: +62.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 179
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 590.58ms

### Efficiency Metrics

- **Requests/sec**: 2.98
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 590.5800145431604,
    "baseline_value": 364.12102149592505,
    "deviation": 1.656736247712116,
    "severity": "warning",
    "percentage_change": 62.19333124928347
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 179,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 590.5800145431604
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.9833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
