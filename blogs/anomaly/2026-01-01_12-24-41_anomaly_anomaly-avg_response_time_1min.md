---
timestamp: 1767288281.568915
datetime: '2026-01-01T12:24:41.568915'
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
  anomaly_id: avg_response_time_1min_1767288281.568915
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1225.023783577813
    baseline_value: 534.5556085759944
    deviation: 2.177043135848951
    severity: warning
    percentage_change: 129.16676280717746
  system_state:
    active_requests: 3
    completed_requests_1min: 90
    error_rate_1min: 0.0
    avg_response_time_1min: 1225.023783577813
  metadata: {}
  efficiency:
    requests_per_second: 1.5
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1225.02
- **Baseline Value**: 534.56
- **Deviation**: 2.18 standard deviations
- **Change**: +129.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 90
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1225.02ms

### Efficiency Metrics

- **Requests/sec**: 1.50
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1225.023783577813,
    "baseline_value": 534.5556085759944,
    "deviation": 2.177043135848951,
    "severity": "warning",
    "percentage_change": 129.16676280717746
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 90,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1225.023783577813
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
