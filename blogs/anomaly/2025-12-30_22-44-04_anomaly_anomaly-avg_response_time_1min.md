---
timestamp: 1767152644.509038
datetime: '2025-12-30T22:44:04.509038'
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
  anomaly_id: avg_response_time_1min_1767152644.509038
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 91.10754444485619
    baseline_value: 85.23501210267159
    deviation: 2.062327967536904
    severity: warning
    percentage_change: 6.8898122934630655
  system_state:
    active_requests: 0
    completed_requests_1min: 126
    error_rate_1min: 0.0
    avg_response_time_1min: 91.10754444485619
  metadata: {}
  efficiency:
    requests_per_second: 2.1
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 91.11
- **Baseline Value**: 85.24
- **Deviation**: 2.06 standard deviations
- **Change**: +6.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 126
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 91.11ms

### Efficiency Metrics

- **Requests/sec**: 2.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 91.10754444485619,
    "baseline_value": 85.23501210267159,
    "deviation": 2.062327967536904,
    "severity": "warning",
    "percentage_change": 6.8898122934630655
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 126,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 91.10754444485619
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
