---
timestamp: 1767442648.7108989
datetime: '2026-01-03T07:17:28.710899'
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
  anomaly_id: avg_response_time_1min_1767442648.7108989
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 539.6761869129382
    baseline_value: 569.9944284306952
    deviation: 1.5626139265961514
    severity: warning
    percentage_change: -5.319041731904109
  system_state:
    active_requests: 6
    completed_requests_1min: 665
    error_rate_1min: 0.0
    avg_response_time_1min: 539.6761869129382
  metadata: {}
  efficiency:
    requests_per_second: 11.083333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 539.68
- **Baseline Value**: 569.99
- **Deviation**: 1.56 standard deviations
- **Change**: -5.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 665
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 539.68ms

### Efficiency Metrics

- **Requests/sec**: 11.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 539.6761869129382,
    "baseline_value": 569.9944284306952,
    "deviation": 1.5626139265961514,
    "severity": "warning",
    "percentage_change": -5.319041731904109
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 665,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 539.6761869129382
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.083333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
