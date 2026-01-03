---
timestamp: 1767447809.631051
datetime: '2026-01-03T08:43:29.631051'
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
  anomaly_id: avg_response_time_1min_1767447809.631051
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 549.6912882676138
    baseline_value: 533.5765434872536
    deviation: 1.7477617160380288
    severity: warning
    percentage_change: 3.0201374061611355
  system_state:
    active_requests: 6
    completed_requests_1min: 726
    error_rate_1min: 0.0
    avg_response_time_1min: 549.6912882676138
  metadata: {}
  efficiency:
    requests_per_second: 12.1
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 549.69
- **Baseline Value**: 533.58
- **Deviation**: 1.75 standard deviations
- **Change**: +3.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 726
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 549.69ms

### Efficiency Metrics

- **Requests/sec**: 12.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 549.6912882676138,
    "baseline_value": 533.5765434872536,
    "deviation": 1.7477617160380288,
    "severity": "warning",
    "percentage_change": 3.0201374061611355
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 726,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 549.6912882676138
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
