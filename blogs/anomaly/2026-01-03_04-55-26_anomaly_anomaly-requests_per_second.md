---
timestamp: 1767434126.7859452
datetime: '2026-01-03T04:55:26.785945'
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
  anomaly_id: requests_per_second_1767434126.7859452
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.316666666666666
    baseline_value: 11.566666666666666
    deviation: 1.5000000000000053
    severity: warning
    percentage_change: -2.161383285302594
  system_state:
    active_requests: 6
    completed_requests_1min: 679
    error_rate_1min: 0.0
    avg_response_time_1min: 536.4499127215244
  metadata: {}
  efficiency:
    requests_per_second: 11.316666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.32
- **Baseline Value**: 11.57
- **Deviation**: 1.50 standard deviations
- **Change**: -2.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 679
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 536.45ms

### Efficiency Metrics

- **Requests/sec**: 11.32
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.316666666666666,
    "baseline_value": 11.566666666666666,
    "deviation": 1.5000000000000053,
    "severity": "warning",
    "percentage_change": -2.161383285302594
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 679,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 536.4499127215244
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.316666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
