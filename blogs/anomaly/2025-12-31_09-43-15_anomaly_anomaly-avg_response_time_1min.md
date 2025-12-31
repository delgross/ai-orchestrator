---
timestamp: 1767192195.583499
datetime: '2025-12-31T09:43:15.583499'
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
  anomaly_id: avg_response_time_1min_1767192195.583499
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 132.67024358113608
    baseline_value: 104.20607216656208
    deviation: 2.672389849096758
    severity: warning
    percentage_change: 27.315271387522515
  system_state:
    active_requests: 0
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 132.67024358113608
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

- **Current Value**: 132.67
- **Baseline Value**: 104.21
- **Deviation**: 2.67 standard deviations
- **Change**: +27.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 132.67ms

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
    "current_value": 132.67024358113608,
    "baseline_value": 104.20607216656208,
    "deviation": 2.672389849096758,
    "severity": "warning",
    "percentage_change": 27.315271387522515
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 132.67024358113608
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
