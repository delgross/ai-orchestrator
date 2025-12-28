---
timestamp: 1766861523.8535402
datetime: '2025-12-27T13:52:03.853540'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
metadata:
  anomaly_id: avg_response_time_1min_1766861523.8535402
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 363.7890249326084
    baseline_value: 142.59800384981577
    deviation: 4.357478082525162
    severity: warning
    percentage_change: 155.11508934988393
  system_state:
    active_requests: 1
    completed_requests_1min: 181
    error_rate_1min: 0.0
    avg_response_time_1min: 363.7890249326084
  metadata: {}
  efficiency:
    requests_per_second: 3.0166666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 363.79
- **Baseline Value**: 142.60
- **Deviation**: 4.36 standard deviations
- **Change**: +155.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 181
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 363.79ms

### Efficiency Metrics

- **Requests/sec**: 3.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 363.7890249326084,
    "baseline_value": 142.59800384981577,
    "deviation": 4.357478082525162,
    "severity": "warning",
    "percentage_change": 155.11508934988393
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 181,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 363.7890249326084
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.0166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
