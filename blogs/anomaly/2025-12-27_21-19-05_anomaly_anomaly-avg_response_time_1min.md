---
timestamp: 1766888345.585414
datetime: '2025-12-27T21:19:05.585414'
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
  anomaly_id: avg_response_time_1min_1766888345.585414
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 378.43141237894696
    baseline_value: 133.26627573377692
    deviation: 5.897701775745762
    severity: warning
    percentage_change: 183.96637506020727
  system_state:
    active_requests: 1
    completed_requests_1min: 75
    error_rate_1min: 0.0
    avg_response_time_1min: 378.43141237894696
  metadata: {}
  efficiency:
    requests_per_second: 1.25
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 378.43
- **Baseline Value**: 133.27
- **Deviation**: 5.90 standard deviations
- **Change**: +184.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 75
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 378.43ms

### Efficiency Metrics

- **Requests/sec**: 1.25
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
    "current_value": 378.43141237894696,
    "baseline_value": 133.26627573377692,
    "deviation": 5.897701775745762,
    "severity": "warning",
    "percentage_change": 183.96637506020727
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 75,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 378.43141237894696
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.25,
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
