---
timestamp: 1767369091.066259
datetime: '2026-01-02T10:51:31.066259'
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
  anomaly_id: avg_response_time_1min_1767369091.066259
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4275.361065986829
    baseline_value: 2124.4399576563965
    deviation: 2.484542643776748
    severity: warning
    percentage_change: 101.24650031075714
  system_state:
    active_requests: 11
    completed_requests_1min: 195
    error_rate_1min: 0.0
    avg_response_time_1min: 4275.361065986829
  metadata: {}
  efficiency:
    requests_per_second: 3.25
    cache_hit_rate: 0.0
    queue_depth: 11
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4275.36
- **Baseline Value**: 2124.44
- **Deviation**: 2.48 standard deviations
- **Change**: +101.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 11
- **Completed Requests (1min)**: 195
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4275.36ms

### Efficiency Metrics

- **Requests/sec**: 3.25
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
    "current_value": 4275.361065986829,
    "baseline_value": 2124.4399576563965,
    "deviation": 2.484542643776748,
    "severity": "warning",
    "percentage_change": 101.24650031075714
  },
  "system_state": {
    "active_requests": 11,
    "completed_requests_1min": 195,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4275.361065986829
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.25,
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
