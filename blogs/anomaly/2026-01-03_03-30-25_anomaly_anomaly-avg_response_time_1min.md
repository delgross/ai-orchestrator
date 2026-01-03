---
timestamp: 1767429025.678198
datetime: '2026-01-03T03:30:25.678198'
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
  anomaly_id: avg_response_time_1min_1767429025.678198
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 540.0253412966243
    baseline_value: 530.4789827727161
    deviation: 1.5610717330195254
    severity: warning
    percentage_change: 1.7995733731072934
  system_state:
    active_requests: 6
    completed_requests_1min: 668
    error_rate_1min: 0.0
    avg_response_time_1min: 540.0253412966243
  metadata: {}
  efficiency:
    requests_per_second: 11.133333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 540.03
- **Baseline Value**: 530.48
- **Deviation**: 1.56 standard deviations
- **Change**: +1.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 668
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 540.03ms

### Efficiency Metrics

- **Requests/sec**: 11.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 540.0253412966243,
    "baseline_value": 530.4789827727161,
    "deviation": 1.5610717330195254,
    "severity": "warning",
    "percentage_change": 1.7995733731072934
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 668,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 540.0253412966243
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.133333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
