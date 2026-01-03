---
timestamp: 1767430225.953347
datetime: '2026-01-03T03:50:25.953347'
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
  anomaly_id: requests_per_second_1767430225.953347
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.1
    baseline_value: 11.333333333333334
    deviation: 2.3333333333333512
    severity: warning
    percentage_change: -2.058823529411773
  system_state:
    active_requests: 6
    completed_requests_1min: 666
    error_rate_1min: 0.0
    avg_response_time_1min: 533.9475673240227
  metadata: {}
  efficiency:
    requests_per_second: 11.1
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.10
- **Baseline Value**: 11.33
- **Deviation**: 2.33 standard deviations
- **Change**: -2.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 666
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 533.95ms

### Efficiency Metrics

- **Requests/sec**: 11.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.1,
    "baseline_value": 11.333333333333334,
    "deviation": 2.3333333333333512,
    "severity": "warning",
    "percentage_change": -2.058823529411773
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 666,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 533.9475673240227
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
