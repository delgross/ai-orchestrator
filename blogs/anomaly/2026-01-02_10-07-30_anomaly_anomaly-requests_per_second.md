---
timestamp: 1767366450.433182
datetime: '2026-01-02T10:07:30.433182'
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
  anomaly_id: requests_per_second_1767366450.433182
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.566666666666666
    baseline_value: 6.2
    deviation: 2.5637583892617446
    severity: warning
    percentage_change: 102.68817204301075
  system_state:
    active_requests: 12
    completed_requests_1min: 754
    error_rate_1min: 0.0
    avg_response_time_1min: 1221.0619085979715
  metadata: {}
  efficiency:
    requests_per_second: 12.566666666666666
    cache_hit_rate: 0.0
    queue_depth: 12
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.57
- **Baseline Value**: 6.20
- **Deviation**: 2.56 standard deviations
- **Change**: +102.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 12
- **Completed Requests (1min)**: 754
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1221.06ms

### Efficiency Metrics

- **Requests/sec**: 12.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 12

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.566666666666666,
    "baseline_value": 6.2,
    "deviation": 2.5637583892617446,
    "severity": "warning",
    "percentage_change": 102.68817204301075
  },
  "system_state": {
    "active_requests": 12,
    "completed_requests_1min": 754,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1221.0619085979715
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.566666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 12
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
