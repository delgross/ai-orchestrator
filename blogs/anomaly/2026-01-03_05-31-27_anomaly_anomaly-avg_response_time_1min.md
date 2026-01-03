---
timestamp: 1767436287.226012
datetime: '2026-01-03T05:31:27.226012'
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
  anomaly_id: avg_response_time_1min_1767436287.226012
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 586.6532187582302
    baseline_value: 546.9869030612057
    deviation: 1.8803110565702985
    severity: warning
    percentage_change: 7.2517852758507475
  system_state:
    active_requests: 7
    completed_requests_1min: 673
    error_rate_1min: 0.0
    avg_response_time_1min: 586.6532187582302
  metadata: {}
  efficiency:
    requests_per_second: 11.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 586.65
- **Baseline Value**: 546.99
- **Deviation**: 1.88 standard deviations
- **Change**: +7.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 673
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 586.65ms

### Efficiency Metrics

- **Requests/sec**: 11.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 586.6532187582302,
    "baseline_value": 546.9869030612057,
    "deviation": 1.8803110565702985,
    "severity": "warning",
    "percentage_change": 7.2517852758507475
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 673,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 586.6532187582302
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.216666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
