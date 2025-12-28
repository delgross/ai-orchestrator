---
timestamp: 1766887505.536439
datetime: '2025-12-27T21:05:05.536439'
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
  anomaly_id: avg_response_time_1min_1766887505.536439
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 271.42635981241864
    baseline_value: 129.77809926751692
    deviation: 4.448268246000172
    severity: warning
    percentage_change: 109.14650572352454
  system_state:
    active_requests: 2
    completed_requests_1min: 81
    error_rate_1min: 0.0
    avg_response_time_1min: 271.42635981241864
  metadata: {}
  efficiency:
    requests_per_second: 1.35
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 271.43
- **Baseline Value**: 129.78
- **Deviation**: 4.45 standard deviations
- **Change**: +109.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 81
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 271.43ms

### Efficiency Metrics

- **Requests/sec**: 1.35
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 271.42635981241864,
    "baseline_value": 129.77809926751692,
    "deviation": 4.448268246000172,
    "severity": "warning",
    "percentage_change": 109.14650572352454
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 81,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 271.42635981241864
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.35,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
