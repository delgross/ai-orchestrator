---
timestamp: 1766865304.150638
datetime: '2025-12-27T14:55:04.150638'
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
  anomaly_id: avg_response_time_1min_1766865304.150638
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 23.61933101307262
    baseline_value: 127.07054155622129
    deviation: 13.587635720576609
    severity: critical
    percentage_change: -81.41242594561349
  system_state:
    active_requests: 0
    completed_requests_1min: 55
    error_rate_1min: 0.0
    avg_response_time_1min: 23.61933101307262
  metadata: {}
  efficiency:
    requests_per_second: 0.9166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 23.62
- **Baseline Value**: 127.07
- **Deviation**: 13.59 standard deviations
- **Change**: -81.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 55
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 23.62ms

### Efficiency Metrics

- **Requests/sec**: 0.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 23.61933101307262,
    "baseline_value": 127.07054155622129,
    "deviation": 13.587635720576609,
    "severity": "critical",
    "percentage_change": -81.41242594561349
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 55,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 23.61933101307262
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
