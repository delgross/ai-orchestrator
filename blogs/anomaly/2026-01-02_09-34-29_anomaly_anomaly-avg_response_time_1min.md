---
timestamp: 1767364469.8482099
datetime: '2026-01-02T09:34:29.848210'
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
- Consider increasing concurrency limits or scaling resources
metadata:
  anomaly_id: avg_response_time_1min_1767364469.8482099
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 252535.62092781067
    baseline_value: 73948.90960525064
    deviation: 2.7498200691754078
    severity: warning
    percentage_change: 241.5001279611562
  system_state:
    active_requests: 11
    completed_requests_1min: 1
    error_rate_1min: 0.0
    avg_response_time_1min: 252535.62092781067
  metadata: {}
  efficiency:
    requests_per_second: 0.016666666666666666
    cache_hit_rate: 0.0
    queue_depth: 11
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 252535.62
- **Baseline Value**: 73948.91
- **Deviation**: 2.75 standard deviations
- **Change**: +241.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 11
- **Completed Requests (1min)**: 1
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 252535.62ms

### Efficiency Metrics

- **Requests/sec**: 0.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 11

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Consider increasing concurrency limits or scaling resources


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 252535.62092781067,
    "baseline_value": 73948.90960525064,
    "deviation": 2.7498200691754078,
    "severity": "warning",
    "percentage_change": 241.5001279611562
  },
  "system_state": {
    "active_requests": 11,
    "completed_requests_1min": 1,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 252535.62092781067
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.016666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 11
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Consider increasing concurrency limits or scaling resources
