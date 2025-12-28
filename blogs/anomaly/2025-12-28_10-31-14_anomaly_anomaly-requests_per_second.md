---
timestamp: 1766935874.268669
datetime: '2025-12-28T10:31:14.268669'
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
  anomaly_id: requests_per_second_1766935874.268669
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.85
    baseline_value: 1.4130681818181818
    deviation: 5.244955625052987
    severity: warning
    percentage_change: 384.76075593084033
  system_state:
    active_requests: 0
    completed_requests_1min: 411
    error_rate_1min: 0.0
    avg_response_time_1min: 220.8501248464097
  metadata: {}
  efficiency:
    requests_per_second: 6.85
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.85
- **Baseline Value**: 1.41
- **Deviation**: 5.24 standard deviations
- **Change**: +384.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 411
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 220.85ms

### Efficiency Metrics

- **Requests/sec**: 6.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.85,
    "baseline_value": 1.4130681818181818,
    "deviation": 5.244955625052987,
    "severity": "warning",
    "percentage_change": 384.76075593084033
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 411,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 220.8501248464097
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
