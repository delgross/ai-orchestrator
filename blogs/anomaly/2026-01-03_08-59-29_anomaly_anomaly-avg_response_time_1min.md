---
timestamp: 1767448769.9490712
datetime: '2026-01-03T08:59:29.949071'
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
  anomaly_id: avg_response_time_1min_1767448769.9490712
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 559.0396217063621
    baseline_value: 529.5044523574401
    deviation: 2.261130687897189
    severity: warning
    percentage_change: 5.577888763243951
  system_state:
    active_requests: 7
    completed_requests_1min: 675
    error_rate_1min: 0.0
    avg_response_time_1min: 559.0396217063621
  metadata: {}
  efficiency:
    requests_per_second: 11.25
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 559.04
- **Baseline Value**: 529.50
- **Deviation**: 2.26 standard deviations
- **Change**: +5.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 675
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 559.04ms

### Efficiency Metrics

- **Requests/sec**: 11.25
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 559.0396217063621,
    "baseline_value": 529.5044523574401,
    "deviation": 2.261130687897189,
    "severity": "warning",
    "percentage_change": 5.577888763243951
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 675,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 559.0396217063621
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.25,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
