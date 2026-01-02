---
timestamp: 1767358771.422587
datetime: '2026-01-02T07:59:31.422587'
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
  anomaly_id: avg_response_time_1min_1767358771.422587
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1029.6244025230408
    baseline_value: 814.5912093582864
    deviation: 1.5061134684361934
    severity: warning
    percentage_change: 26.397681523491016
  system_state:
    active_requests: 2
    completed_requests_1min: 12
    error_rate_1min: 0.0
    avg_response_time_1min: 1029.6244025230408
  metadata: {}
  efficiency:
    requests_per_second: 0.2
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1029.62
- **Baseline Value**: 814.59
- **Deviation**: 1.51 standard deviations
- **Change**: +26.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 12
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1029.62ms

### Efficiency Metrics

- **Requests/sec**: 0.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1029.6244025230408,
    "baseline_value": 814.5912093582864,
    "deviation": 1.5061134684361934,
    "severity": "warning",
    "percentage_change": 26.397681523491016
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 12,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1029.6244025230408
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
