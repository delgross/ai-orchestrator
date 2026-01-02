---
timestamp: 1767336364.2710881
datetime: '2026-01-02T01:46:04.271088'
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
  anomaly_id: avg_response_time_1min_1767336364.2710881
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1877.6227474212646
    baseline_value: 1111.2354755401611
    deviation: 2.5986985411864536
    severity: warning
    percentage_change: 68.9671351167555
  system_state:
    active_requests: 0
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 1877.6227474212646
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1877.62
- **Baseline Value**: 1111.24
- **Deviation**: 2.60 standard deviations
- **Change**: +69.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1877.62ms

### Efficiency Metrics

- **Requests/sec**: 0.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1877.6227474212646,
    "baseline_value": 1111.2354755401611,
    "deviation": 2.5986985411864536,
    "severity": "warning",
    "percentage_change": 68.9671351167555
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1877.6227474212646
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
