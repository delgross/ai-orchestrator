---
timestamp: 1767433166.595236
datetime: '2026-01-03T04:39:26.595236'
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
  anomaly_id: requests_per_second_1767433166.595236
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.566666666666666
    baseline_value: 11.366666666666667
    deviation: 2.3999999999999746
    severity: warning
    percentage_change: 1.7595307917888499
  system_state:
    active_requests: 6
    completed_requests_1min: 694
    error_rate_1min: 0.0
    avg_response_time_1min: 525.0231965474505
  metadata: {}
  efficiency:
    requests_per_second: 11.566666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.57
- **Baseline Value**: 11.37
- **Deviation**: 2.40 standard deviations
- **Change**: +1.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 694
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 525.02ms

### Efficiency Metrics

- **Requests/sec**: 11.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.566666666666666,
    "baseline_value": 11.366666666666667,
    "deviation": 2.3999999999999746,
    "severity": "warning",
    "percentage_change": 1.7595307917888499
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 694,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 525.0231965474505
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.566666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
