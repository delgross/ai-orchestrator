---
timestamp: 1767151924.443732
datetime: '2025-12-30T22:32:04.443732'
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
  anomaly_id: avg_response_time_1min_1767151924.443732
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 96.32107548820325
    baseline_value: 85.23501210267159
    deviation: 3.8932265056481
    severity: critical
    percentage_change: 13.006466605739098
  system_state:
    active_requests: 0
    completed_requests_1min: 313
    error_rate_1min: 0.0
    avg_response_time_1min: 96.32107548820325
  metadata: {}
  efficiency:
    requests_per_second: 5.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 96.32
- **Baseline Value**: 85.24
- **Deviation**: 3.89 standard deviations
- **Change**: +13.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 313
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 96.32ms

### Efficiency Metrics

- **Requests/sec**: 5.22
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
    "current_value": 96.32107548820325,
    "baseline_value": 85.23501210267159,
    "deviation": 3.8932265056481,
    "severity": "critical",
    "percentage_change": 13.006466605739098
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 313,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 96.32107548820325
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.216666666666667,
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
