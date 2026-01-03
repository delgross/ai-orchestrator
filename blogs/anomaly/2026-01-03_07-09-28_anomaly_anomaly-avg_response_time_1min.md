---
timestamp: 1767442168.5813508
datetime: '2026-01-03T07:09:28.581351'
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
  anomaly_id: avg_response_time_1min_1767442168.5813508
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 516.3167533518254
    baseline_value: 529.1807813278693
    deviation: 1.9310010704349778
    severity: warning
    percentage_change: -2.4309325716184134
  system_state:
    active_requests: 6
    completed_requests_1min: 696
    error_rate_1min: 0.0
    avg_response_time_1min: 516.3167533518254
  metadata: {}
  efficiency:
    requests_per_second: 11.6
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 516.32
- **Baseline Value**: 529.18
- **Deviation**: 1.93 standard deviations
- **Change**: -2.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 696
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 516.32ms

### Efficiency Metrics

- **Requests/sec**: 11.60
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 516.3167533518254,
    "baseline_value": 529.1807813278693,
    "deviation": 1.9310010704349778,
    "severity": "warning",
    "percentage_change": -2.4309325716184134
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 696,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 516.3167533518254
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.6,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
