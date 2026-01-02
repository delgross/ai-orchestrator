---
timestamp: 1767341764.960151
datetime: '2026-01-02T03:16:04.960151'
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
  anomaly_id: avg_response_time_1min_1767341764.960151
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 443.98262899103565
    baseline_value: 438.864194828531
    deviation: 1.5584250100645785
    severity: warning
    percentage_change: 1.16629112668999
  system_state:
    active_requests: 6
    completed_requests_1min: 814
    error_rate_1min: 0.0
    avg_response_time_1min: 443.98262899103565
  metadata: {}
  efficiency:
    requests_per_second: 13.566666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 443.98
- **Baseline Value**: 438.86
- **Deviation**: 1.56 standard deviations
- **Change**: +1.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 814
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 443.98ms

### Efficiency Metrics

- **Requests/sec**: 13.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 443.98262899103565,
    "baseline_value": 438.864194828531,
    "deviation": 1.5584250100645785,
    "severity": "warning",
    "percentage_change": 1.16629112668999
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 814,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 443.98262899103565
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.566666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
