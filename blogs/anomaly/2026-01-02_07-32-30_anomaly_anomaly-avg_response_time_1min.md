---
timestamp: 1767357150.941613
datetime: '2026-01-02T07:32:30.941613'
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
  anomaly_id: avg_response_time_1min_1767357150.941613
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 372.7831729387833
    baseline_value: 674.3269898044475
    deviation: 2.153201702019794
    severity: warning
    percentage_change: -44.71774397657001
  system_state:
    active_requests: 1
    completed_requests_1min: 236
    error_rate_1min: 0.0
    avg_response_time_1min: 372.7831729387833
  metadata: {}
  efficiency:
    requests_per_second: 3.933333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 372.78
- **Baseline Value**: 674.33
- **Deviation**: 2.15 standard deviations
- **Change**: -44.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 236
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 372.78ms

### Efficiency Metrics

- **Requests/sec**: 3.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 372.7831729387833,
    "baseline_value": 674.3269898044475,
    "deviation": 2.153201702019794,
    "severity": "warning",
    "percentage_change": -44.71774397657001
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 236,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 372.7831729387833
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.933333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
