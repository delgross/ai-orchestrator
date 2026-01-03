---
timestamp: 1767421249.543257
datetime: '2026-01-03T01:20:49.543257'
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
  anomaly_id: avg_response_time_1min_1767421249.543257
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 581.140274554491
    baseline_value: 437.4743858301361
    deviation: 1.813735307243123
    severity: warning
    percentage_change: 32.8398400861206
  system_state:
    active_requests: 16
    completed_requests_1min: 1600
    error_rate_1min: 0.0
    avg_response_time_1min: 581.140274554491
  metadata: {}
  efficiency:
    requests_per_second: 26.666666666666668
    cache_hit_rate: 0.0
    queue_depth: 16
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 581.14
- **Baseline Value**: 437.47
- **Deviation**: 1.81 standard deviations
- **Change**: +32.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 16
- **Completed Requests (1min)**: 1600
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 581.14ms

### Efficiency Metrics

- **Requests/sec**: 26.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 16

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 581.140274554491,
    "baseline_value": 437.4743858301361,
    "deviation": 1.813735307243123,
    "severity": "warning",
    "percentage_change": 32.8398400861206
  },
  "system_state": {
    "active_requests": 16,
    "completed_requests_1min": 1600,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 581.140274554491
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 26.666666666666668,
    "cache_hit_rate": 0.0,
    "queue_depth": 16
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
