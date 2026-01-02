---
timestamp: 1767300653.463449
datetime: '2026-01-01T15:50:53.463449'
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
  anomaly_id: avg_response_time_1min_1767300653.463449
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 405.6186046600342
    baseline_value: 274.55343546405913
    deviation: 4.975104960758165
    severity: critical
    percentage_change: 47.737581201431496
  system_state:
    active_requests: 0
    completed_requests_1min: 125
    error_rate_1min: 0.0
    avg_response_time_1min: 405.6186046600342
  metadata: {}
  efficiency:
    requests_per_second: 2.0833333333333335
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 405.62
- **Baseline Value**: 274.55
- **Deviation**: 4.98 standard deviations
- **Change**: +47.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 125
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 405.62ms

### Efficiency Metrics

- **Requests/sec**: 2.08
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
    "current_value": 405.6186046600342,
    "baseline_value": 274.55343546405913,
    "deviation": 4.975104960758165,
    "severity": "critical",
    "percentage_change": 47.737581201431496
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 125,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 405.6186046600342
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.0833333333333335,
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
