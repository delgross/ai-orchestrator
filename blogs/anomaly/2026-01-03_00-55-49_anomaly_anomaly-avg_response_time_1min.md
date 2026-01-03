---
timestamp: 1767419749.064461
datetime: '2026-01-03T00:55:49.064461'
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
  anomaly_id: avg_response_time_1min_1767419749.064461
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1041.004718632945
    baseline_value: 847.8010468247006
    deviation: 2.452519377804135
    severity: warning
    percentage_change: 22.788798448864505
  system_state:
    active_requests: 30
    completed_requests_1min: 1719
    error_rate_1min: 0.0
    avg_response_time_1min: 1041.004718632945
  metadata: {}
  efficiency:
    requests_per_second: 28.65
    cache_hit_rate: 0.0
    queue_depth: 30
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1041.00
- **Baseline Value**: 847.80
- **Deviation**: 2.45 standard deviations
- **Change**: +22.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 30
- **Completed Requests (1min)**: 1719
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1041.00ms

### Efficiency Metrics

- **Requests/sec**: 28.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 30

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1041.004718632945,
    "baseline_value": 847.8010468247006,
    "deviation": 2.452519377804135,
    "severity": "warning",
    "percentage_change": 22.788798448864505
  },
  "system_state": {
    "active_requests": 30,
    "completed_requests_1min": 1719,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1041.004718632945
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 28.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 30
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
