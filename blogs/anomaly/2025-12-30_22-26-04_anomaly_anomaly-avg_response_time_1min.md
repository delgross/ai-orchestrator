---
timestamp: 1767151564.392985
datetime: '2025-12-30T22:26:04.392985'
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
  anomaly_id: avg_response_time_1min_1767151564.392985
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 90.35568283154414
    baseline_value: 85.23501210267159
    deviation: 1.7982876621796373
    severity: warning
    percentage_change: 6.0077081032197714
  system_state:
    active_requests: 1
    completed_requests_1min: 1352
    error_rate_1min: 0.0
    avg_response_time_1min: 90.35568283154414
  metadata: {}
  efficiency:
    requests_per_second: 22.533333333333335
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 90.36
- **Baseline Value**: 85.24
- **Deviation**: 1.80 standard deviations
- **Change**: +6.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 1352
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 90.36ms

### Efficiency Metrics

- **Requests/sec**: 22.53
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 90.35568283154414,
    "baseline_value": 85.23501210267159,
    "deviation": 1.7982876621796373,
    "severity": "warning",
    "percentage_change": 6.0077081032197714
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 1352,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 90.35568283154414
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 22.533333333333335,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
