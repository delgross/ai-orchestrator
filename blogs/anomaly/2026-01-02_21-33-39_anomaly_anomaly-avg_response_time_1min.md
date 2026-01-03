---
timestamp: 1767407619.098876
datetime: '2026-01-02T21:33:39.098876'
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
  anomaly_id: avg_response_time_1min_1767407619.098876
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 492.84610033363225
    baseline_value: 433.19272504896463
    deviation: 20.253420483222005
    severity: critical
    percentage_change: 13.77063183088425
  system_state:
    active_requests: 6
    completed_requests_1min: 727
    error_rate_1min: 0.0
    avg_response_time_1min: 492.84610033363225
  metadata: {}
  efficiency:
    requests_per_second: 12.116666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 492.85
- **Baseline Value**: 433.19
- **Deviation**: 20.25 standard deviations
- **Change**: +13.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 727
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 492.85ms

### Efficiency Metrics

- **Requests/sec**: 12.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 492.84610033363225,
    "baseline_value": 433.19272504896463,
    "deviation": 20.253420483222005,
    "severity": "critical",
    "percentage_change": 13.77063183088425
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 727,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 492.84610033363225
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.116666666666667,
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
