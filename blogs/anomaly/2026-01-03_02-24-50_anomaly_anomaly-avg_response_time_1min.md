---
timestamp: 1767425090.5196512
datetime: '2026-01-03T02:24:50.519651'
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
  anomaly_id: avg_response_time_1min_1767425090.5196512
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 564.8173310409528
    baseline_value: 477.93956144342144
    deviation: 1.5978370373529194
    severity: warning
    percentage_change: 18.177563986365243
  system_state:
    active_requests: 8
    completed_requests_1min: 831
    error_rate_1min: 0.0
    avg_response_time_1min: 564.8173310409528
  metadata: {}
  efficiency:
    requests_per_second: 13.85
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 564.82
- **Baseline Value**: 477.94
- **Deviation**: 1.60 standard deviations
- **Change**: +18.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 831
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 564.82ms

### Efficiency Metrics

- **Requests/sec**: 13.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 564.8173310409528,
    "baseline_value": 477.93956144342144,
    "deviation": 1.5978370373529194,
    "severity": "warning",
    "percentage_change": 18.177563986365243
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 831,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 564.8173310409528
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
