---
timestamp: 1767425873.918505
datetime: '2026-01-03T02:37:53.918505'
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
  anomaly_id: avg_response_time_1min_1767425873.918505
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 446.1248917961349
    baseline_value: 423.28812087726817
    deviation: 2.2424761894468914
    severity: warning
    percentage_change: 5.3950890167995516
  system_state:
    active_requests: 8
    completed_requests_1min: 837
    error_rate_1min: 0.0
    avg_response_time_1min: 446.1248917961349
  metadata: {}
  efficiency:
    requests_per_second: 13.95
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 446.12
- **Baseline Value**: 423.29
- **Deviation**: 2.24 standard deviations
- **Change**: +5.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 837
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 446.12ms

### Efficiency Metrics

- **Requests/sec**: 13.95
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 446.1248917961349,
    "baseline_value": 423.28812087726817,
    "deviation": 2.2424761894468914,
    "severity": "warning",
    "percentage_change": 5.3950890167995516
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 837,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 446.1248917961349
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.95,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
