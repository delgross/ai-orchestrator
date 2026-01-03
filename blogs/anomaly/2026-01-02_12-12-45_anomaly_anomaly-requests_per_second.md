---
timestamp: 1767373965.266963
datetime: '2026-01-02T12:12:45.266963'
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
  anomaly_id: requests_per_second_1767373965.266963
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.55
    baseline_value: 13.416666666666666
    deviation: 1.6000000000000383
    severity: warning
    percentage_change: 0.9937888198757862
  system_state:
    active_requests: 7
    completed_requests_1min: 813
    error_rate_1min: 0.0
    avg_response_time_1min: 688.5227019203252
  metadata: {}
  efficiency:
    requests_per_second: 13.55
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.55
- **Baseline Value**: 13.42
- **Deviation**: 1.60 standard deviations
- **Change**: +1.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 813
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 688.52ms

### Efficiency Metrics

- **Requests/sec**: 13.55
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.55,
    "baseline_value": 13.416666666666666,
    "deviation": 1.6000000000000383,
    "severity": "warning",
    "percentage_change": 0.9937888198757862
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 813,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 688.5227019203252
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.55,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
