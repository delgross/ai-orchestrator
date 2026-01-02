---
timestamp: 1767349566.065662
datetime: '2026-01-02T05:26:06.065662'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767349566.065662
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.416666666666666
    baseline_value: 13.783333333333333
    deviation: 4.399999999999975
    severity: critical
    percentage_change: -2.660217654171708
  system_state:
    active_requests: 6
    completed_requests_1min: 805
    error_rate_1min: 0.0
    avg_response_time_1min: 448.90068539921543
  metadata: {}
  efficiency:
    requests_per_second: 13.416666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.42
- **Baseline Value**: 13.78
- **Deviation**: 4.40 standard deviations
- **Change**: -2.7%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 805
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 448.90ms

### Efficiency Metrics

- **Requests/sec**: 13.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.416666666666666,
    "baseline_value": 13.783333333333333,
    "deviation": 4.399999999999975,
    "severity": "critical",
    "percentage_change": -2.660217654171708
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 805,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 448.90068539921543
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.416666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
