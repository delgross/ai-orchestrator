---
timestamp: 1767410985.045685
datetime: '2026-01-02T22:29:45.045685'
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
  anomaly_id: avg_response_time_1min_1767410985.045685
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 59741.901874542236
    baseline_value: 22181.487262248993
    deviation: 1.6933226419049852
    severity: warning
    percentage_change: 169.3322641904985
  system_state:
    active_requests: 1
    completed_requests_1min: 1
    error_rate_1min: 0.0
    avg_response_time_1min: 59741.901874542236
  metadata: {}
  efficiency:
    requests_per_second: 0.016666666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 59741.90
- **Baseline Value**: 22181.49
- **Deviation**: 1.69 standard deviations
- **Change**: +169.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 1
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 59741.90ms

### Efficiency Metrics

- **Requests/sec**: 0.02
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
    "current_value": 59741.901874542236,
    "baseline_value": 22181.487262248993,
    "deviation": 1.6933226419049852,
    "severity": "warning",
    "percentage_change": 169.3322641904985
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 1,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 59741.901874542236
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.016666666666666666,
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
