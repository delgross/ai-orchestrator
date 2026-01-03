---
timestamp: 1767421609.652983
datetime: '2026-01-03T01:26:49.652983'
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
  anomaly_id: requests_per_second_1767421609.652983
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.066666666666666
    baseline_value: 13.55
    deviation: 1.8235294117647034
    severity: warning
    percentage_change: 3.8130381303812966
  system_state:
    active_requests: 7
    completed_requests_1min: 844
    error_rate_1min: 0.0
    avg_response_time_1min: 467.8610292091189
  metadata: {}
  efficiency:
    requests_per_second: 14.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.07
- **Baseline Value**: 13.55
- **Deviation**: 1.82 standard deviations
- **Change**: +3.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 844
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 467.86ms

### Efficiency Metrics

- **Requests/sec**: 14.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.066666666666666,
    "baseline_value": 13.55,
    "deviation": 1.8235294117647034,
    "severity": "warning",
    "percentage_change": 3.8130381303812966
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 844,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 467.8610292091189
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.066666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
