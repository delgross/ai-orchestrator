---
timestamp: 1767042261.746933
datetime: '2025-12-29T16:04:21.746933'
category: anomaly
severity: warning
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: active_requests_1767042261.746933
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 6.0
    baseline_value: 0.36217948717948717
    deviation: 4.371641000699889
    severity: warning
    percentage_change: 1556.637168141593
  system_state:
    active_requests: 6
    completed_requests_1min: 1
    error_rate_1min: 0.0
    avg_response_time_1min: 1.9640922546386719
  metadata: {}
  efficiency:
    requests_per_second: 0.016666666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 6.00
- **Baseline Value**: 0.36
- **Deviation**: 4.37 standard deviations
- **Change**: +1556.6%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 1
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1.96ms

### Efficiency Metrics

- **Requests/sec**: 0.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 6.0,
    "baseline_value": 0.36217948717948717,
    "deviation": 4.371641000699889,
    "severity": "warning",
    "percentage_change": 1556.637168141593
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 1,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1.9640922546386719
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.016666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
