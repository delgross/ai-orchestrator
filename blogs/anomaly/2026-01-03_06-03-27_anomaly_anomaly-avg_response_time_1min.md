---
timestamp: 1767438207.600956
datetime: '2026-01-03T06:03:27.600956'
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
  anomaly_id: avg_response_time_1min_1767438207.600956
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 513.444598627762
    baseline_value: 526.6458902673708
    deviation: 2.9385606216705544
    severity: warning
    percentage_change: -2.5066732473515745
  system_state:
    active_requests: 6
    completed_requests_1min: 710
    error_rate_1min: 0.0
    avg_response_time_1min: 513.444598627762
  metadata: {}
  efficiency:
    requests_per_second: 11.833333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 513.44
- **Baseline Value**: 526.65
- **Deviation**: 2.94 standard deviations
- **Change**: -2.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 710
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 513.44ms

### Efficiency Metrics

- **Requests/sec**: 11.83
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 513.444598627762,
    "baseline_value": 526.6458902673708,
    "deviation": 2.9385606216705544,
    "severity": "warning",
    "percentage_change": -2.5066732473515745
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 710,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 513.444598627762
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
