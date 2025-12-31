---
timestamp: 1767191535.529661
datetime: '2025-12-31T09:32:15.529661'
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
  anomaly_id: avg_response_time_1min_1767191535.529661
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 133.40707619984946
    baseline_value: 103.52323576807976
    deviation: 2.8849864796492852
    severity: warning
    percentage_change: 28.866795178927408
  system_state:
    active_requests: 0
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 133.40707619984946
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 133.41
- **Baseline Value**: 103.52
- **Deviation**: 2.88 standard deviations
- **Change**: +28.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 133.41ms

### Efficiency Metrics

- **Requests/sec**: 0.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 133.40707619984946,
    "baseline_value": 103.52323576807976,
    "deviation": 2.8849864796492852,
    "severity": "warning",
    "percentage_change": 28.866795178927408
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 133.40707619984946
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
