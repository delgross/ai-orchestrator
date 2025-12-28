---
timestamp: 1766933654.101856
datetime: '2025-12-28T09:54:14.101856'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1766933654.101856
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.4
    baseline_value: 0.8956967213114754
    deviation: 4.910460115995643
    severity: warning
    percentage_change: 56.302905513612444
  system_state:
    active_requests: 0
    completed_requests_1min: 84
    error_rate_1min: 0.0
    avg_response_time_1min: 58.90088138126192
  metadata: {}
  efficiency:
    requests_per_second: 1.4
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.40
- **Baseline Value**: 0.90
- **Deviation**: 4.91 standard deviations
- **Change**: +56.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 84
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 58.90ms

### Efficiency Metrics

- **Requests/sec**: 1.40
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.4,
    "baseline_value": 0.8956967213114754,
    "deviation": 4.910460115995643,
    "severity": "warning",
    "percentage_change": 56.302905513612444
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 84,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 58.90088138126192
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.4,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
