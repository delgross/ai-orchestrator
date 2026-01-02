---
timestamp: 1767309012.3853152
datetime: '2026-01-01T18:10:12.385315'
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
  anomaly_id: avg_response_time_1min_1767309012.3853152
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 332.7368851365714
    baseline_value: 277.5013597388017
    deviation: 2.9021140196981308
    severity: warning
    percentage_change: 19.904596305315472
  system_state:
    active_requests: 0
    completed_requests_1min: 145
    error_rate_1min: 0.0
    avg_response_time_1min: 332.7368851365714
  metadata: {}
  efficiency:
    requests_per_second: 2.4166666666666665
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 332.74
- **Baseline Value**: 277.50
- **Deviation**: 2.90 standard deviations
- **Change**: +19.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 145
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 332.74ms

### Efficiency Metrics

- **Requests/sec**: 2.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 332.7368851365714,
    "baseline_value": 277.5013597388017,
    "deviation": 2.9021140196981308,
    "severity": "warning",
    "percentage_change": 19.904596305315472
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 145,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 332.7368851365714
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.4166666666666665,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
