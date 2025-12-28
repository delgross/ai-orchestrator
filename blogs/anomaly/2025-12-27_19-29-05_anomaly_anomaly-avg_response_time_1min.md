---
timestamp: 1766881745.2324321
datetime: '2025-12-27T19:29:05.232432'
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
  anomaly_id: avg_response_time_1min_1766881745.2324321
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 174.835155804952
    baseline_value: 129.3283459123579
    deviation: 5.007900398807899
    severity: warning
    percentage_change: 35.187034653201835
  system_state:
    active_requests: 0
    completed_requests_1min: 150
    error_rate_1min: 0.0
    avg_response_time_1min: 174.835155804952
  metadata: {}
  efficiency:
    requests_per_second: 2.5
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 174.84
- **Baseline Value**: 129.33
- **Deviation**: 5.01 standard deviations
- **Change**: +35.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 150
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 174.84ms

### Efficiency Metrics

- **Requests/sec**: 2.50
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 174.835155804952,
    "baseline_value": 129.3283459123579,
    "deviation": 5.007900398807899,
    "severity": "warning",
    "percentage_change": 35.187034653201835
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 150,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 174.835155804952
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.5,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
