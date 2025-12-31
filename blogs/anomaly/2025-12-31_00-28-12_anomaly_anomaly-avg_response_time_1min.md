---
timestamp: 1767158892.203737
datetime: '2025-12-31T00:28:12.203737'
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
  anomaly_id: avg_response_time_1min_1767158892.203737
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 175.60686910055517
    baseline_value: 121.34474855128343
    deviation: 2.121830730134359
    severity: warning
    percentage_change: 44.717320854094616
  system_state:
    active_requests: 0
    completed_requests_1min: 123
    error_rate_1min: 0.0
    avg_response_time_1min: 175.60686910055517
  metadata: {}
  efficiency:
    requests_per_second: 2.05
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 175.61
- **Baseline Value**: 121.34
- **Deviation**: 2.12 standard deviations
- **Change**: +44.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 123
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 175.61ms

### Efficiency Metrics

- **Requests/sec**: 2.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 175.60686910055517,
    "baseline_value": 121.34474855128343,
    "deviation": 2.121830730134359,
    "severity": "warning",
    "percentage_change": 44.717320854094616
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 123,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 175.60686910055517
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
