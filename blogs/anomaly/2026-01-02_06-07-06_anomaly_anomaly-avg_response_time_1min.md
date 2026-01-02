---
timestamp: 1767352026.488456
datetime: '2026-01-02T06:07:06.488456'
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
  anomaly_id: avg_response_time_1min_1767352026.488456
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 498.2847207122379
    baseline_value: 458.1706319619859
    deviation: 2.5204041505920536
    severity: warning
    percentage_change: 8.755272807092583
  system_state:
    active_requests: 7
    completed_requests_1min: 792
    error_rate_1min: 0.0
    avg_response_time_1min: 498.2847207122379
  metadata: {}
  efficiency:
    requests_per_second: 13.2
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 498.28
- **Baseline Value**: 458.17
- **Deviation**: 2.52 standard deviations
- **Change**: +8.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 792
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 498.28ms

### Efficiency Metrics

- **Requests/sec**: 13.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 498.2847207122379,
    "baseline_value": 458.1706319619859,
    "deviation": 2.5204041505920536,
    "severity": "warning",
    "percentage_change": 8.755272807092583
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 792,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 498.2847207122379
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
