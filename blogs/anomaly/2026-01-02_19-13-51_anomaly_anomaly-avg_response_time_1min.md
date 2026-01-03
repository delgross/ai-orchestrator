---
timestamp: 1767399231.495137
datetime: '2026-01-02T19:13:51.495137'
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
  anomaly_id: avg_response_time_1min_1767399231.495137
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 422.40503114812515
    baseline_value: 418.2785827241022
    deviation: 1.709104798331676
    severity: warning
    percentage_change: 0.986531128882774
  system_state:
    active_requests: 6
    completed_requests_1min: 850
    error_rate_1min: 0.0
    avg_response_time_1min: 422.40503114812515
  metadata: {}
  efficiency:
    requests_per_second: 14.166666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 422.41
- **Baseline Value**: 418.28
- **Deviation**: 1.71 standard deviations
- **Change**: +1.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 850
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 422.41ms

### Efficiency Metrics

- **Requests/sec**: 14.17
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 422.40503114812515,
    "baseline_value": 418.2785827241022,
    "deviation": 1.709104798331676,
    "severity": "warning",
    "percentage_change": 0.986531128882774
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 850,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 422.40503114812515
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
