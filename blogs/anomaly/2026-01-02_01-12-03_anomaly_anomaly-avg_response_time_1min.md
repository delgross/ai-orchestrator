---
timestamp: 1767334323.996476
datetime: '2026-01-02T01:12:03.996476'
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
  anomaly_id: avg_response_time_1min_1767334323.996476
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1595.8913167317708
    baseline_value: 1084.476661682129
    deviation: 1.9071738241192424
    severity: warning
    percentage_change: 47.15773728651642
  system_state:
    active_requests: 0
    completed_requests_1min: 3
    error_rate_1min: 0.0
    avg_response_time_1min: 1595.8913167317708
  metadata: {}
  efficiency:
    requests_per_second: 0.05
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1595.89
- **Baseline Value**: 1084.48
- **Deviation**: 1.91 standard deviations
- **Change**: +47.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 3
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1595.89ms

### Efficiency Metrics

- **Requests/sec**: 0.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1595.8913167317708,
    "baseline_value": 1084.476661682129,
    "deviation": 1.9071738241192424,
    "severity": "warning",
    "percentage_change": 47.15773728651642
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 3,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1595.8913167317708
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
