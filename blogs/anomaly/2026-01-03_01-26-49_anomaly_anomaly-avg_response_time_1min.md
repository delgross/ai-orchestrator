---
timestamp: 1767421609.6264472
datetime: '2026-01-03T01:26:49.626447'
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
  anomaly_id: avg_response_time_1min_1767421609.6264472
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 467.8610292091189
    baseline_value: 452.1636223281918
    deviation: 1.5866168325796053
    severity: warning
    percentage_change: 3.4716209145930583
  system_state:
    active_requests: 7
    completed_requests_1min: 844
    error_rate_1min: 0.0
    avg_response_time_1min: 467.8610292091189
  metadata: {}
  efficiency:
    requests_per_second: 14.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 467.86
- **Baseline Value**: 452.16
- **Deviation**: 1.59 standard deviations
- **Change**: +3.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 844
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 467.86ms

### Efficiency Metrics

- **Requests/sec**: 14.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 467.8610292091189,
    "baseline_value": 452.1636223281918,
    "deviation": 1.5866168325796053,
    "severity": "warning",
    "percentage_change": 3.4716209145930583
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 844,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 467.8610292091189
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.066666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
