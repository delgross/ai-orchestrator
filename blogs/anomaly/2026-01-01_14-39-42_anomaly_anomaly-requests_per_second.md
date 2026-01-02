---
timestamp: 1767296382.304099
datetime: '2026-01-01T14:39:42.304099'
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
  anomaly_id: requests_per_second_1767296382.304099
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.55
    baseline_value: 13.366666666666667
    deviation: 1.5714285714285672
    severity: warning
    percentage_change: 1.3715710723192036
  system_state:
    active_requests: 9
    completed_requests_1min: 813
    error_rate_1min: 0.0
    avg_response_time_1min: 1215.3641230359142
  metadata: {}
  efficiency:
    requests_per_second: 13.55
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.55
- **Baseline Value**: 13.37
- **Deviation**: 1.57 standard deviations
- **Change**: +1.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 813
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1215.36ms

### Efficiency Metrics

- **Requests/sec**: 13.55
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.55,
    "baseline_value": 13.366666666666667,
    "deviation": 1.5714285714285672,
    "severity": "warning",
    "percentage_change": 1.3715710723192036
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 813,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1215.3641230359142
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.55,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
