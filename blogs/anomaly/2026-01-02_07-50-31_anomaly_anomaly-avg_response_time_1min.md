---
timestamp: 1767358231.278379
datetime: '2026-01-02T07:50:31.278379'
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
  anomaly_id: avg_response_time_1min_1767358231.278379
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 252.52553628336997
    baseline_value: 673.0957151663424
    deviation: 2.970559226056414
    severity: warning
    percentage_change: -62.48296778698654
  system_state:
    active_requests: 0
    completed_requests_1min: 248
    error_rate_1min: 0.0
    avg_response_time_1min: 252.52553628336997
  metadata: {}
  efficiency:
    requests_per_second: 4.133333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 252.53
- **Baseline Value**: 673.10
- **Deviation**: 2.97 standard deviations
- **Change**: -62.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 248
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 252.53ms

### Efficiency Metrics

- **Requests/sec**: 4.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 252.52553628336997,
    "baseline_value": 673.0957151663424,
    "deviation": 2.970559226056414,
    "severity": "warning",
    "percentage_change": -62.48296778698654
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 248,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 252.52553628336997
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.133333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
