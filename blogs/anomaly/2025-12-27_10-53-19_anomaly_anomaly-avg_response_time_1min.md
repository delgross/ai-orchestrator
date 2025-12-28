---
timestamp: 1766850799.573489
datetime: '2025-12-27T10:53:19.573489'
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
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Consider increasing concurrency limits or scaling resources
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1766850799.573489
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 683.9418444834964
    baseline_value: 9.925262928633861
    deviation: 23.126145700406802
    severity: critical
    percentage_change: 6790.919156512824
  system_state:
    active_requests: 104
    completed_requests_1min: 142
    error_rate_1min: 0.0
    avg_response_time_1min: 683.9418444834964
  metadata: {}
  efficiency:
    requests_per_second: 2.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 104
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 683.94
- **Baseline Value**: 9.93
- **Deviation**: 23.13 standard deviations
- **Change**: +6790.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 104
- **Completed Requests (1min)**: 142
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 683.94ms

### Efficiency Metrics

- **Requests/sec**: 2.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 104

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Consider increasing concurrency limits or scaling resources
4. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 683.9418444834964,
    "baseline_value": 9.925262928633861,
    "deviation": 23.126145700406802,
    "severity": "critical",
    "percentage_change": 6790.919156512824
  },
  "system_state": {
    "active_requests": 104,
    "completed_requests_1min": 142,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 683.9418444834964
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.3666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 104
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
4. Investigate immediately - critical system issue detected
