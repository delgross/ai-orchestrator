---
timestamp: 1767416867.757744
datetime: '2026-01-03T00:07:47.757744'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767416867.757744
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1075.0314897638648
    baseline_value: 826.0611382541277
    deviation: 7.657795899438026
    severity: critical
    percentage_change: 30.1394582047442
  system_state:
    active_requests: 33
    completed_requests_1min: 1561
    error_rate_1min: 0.0
    avg_response_time_1min: 1075.0314897638648
  metadata: {}
  efficiency:
    requests_per_second: 26.016666666666666
    cache_hit_rate: 0.0
    queue_depth: 33
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1075.03
- **Baseline Value**: 826.06
- **Deviation**: 7.66 standard deviations
- **Change**: +30.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 33
- **Completed Requests (1min)**: 1561
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1075.03ms

### Efficiency Metrics

- **Requests/sec**: 26.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 33

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1075.0314897638648,
    "baseline_value": 826.0611382541277,
    "deviation": 7.657795899438026,
    "severity": "critical",
    "percentage_change": 30.1394582047442
  },
  "system_state": {
    "active_requests": 33,
    "completed_requests_1min": 1561,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1075.0314897638648
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 26.016666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 33
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
