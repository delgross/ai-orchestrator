---
timestamp: 1767405938.820023
datetime: '2026-01-02T21:05:38.820023'
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
  anomaly_id: avg_response_time_1min_1767405938.820023
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 951.7293996031179
    baseline_value: 477.55569394897014
    deviation: 3.509041314040542
    severity: critical
    percentage_change: 99.29181280054348
  system_state:
    active_requests: 2
    completed_requests_1min: 159
    error_rate_1min: 0.0
    avg_response_time_1min: 951.7293996031179
  metadata: {}
  efficiency:
    requests_per_second: 2.65
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 951.73
- **Baseline Value**: 477.56
- **Deviation**: 3.51 standard deviations
- **Change**: +99.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 159
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 951.73ms

### Efficiency Metrics

- **Requests/sec**: 2.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 951.7293996031179,
    "baseline_value": 477.55569394897014,
    "deviation": 3.509041314040542,
    "severity": "critical",
    "percentage_change": 99.29181280054348
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 159,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 951.7293996031179
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
