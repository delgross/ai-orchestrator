---
timestamp: 1766850799.573494
datetime: '2025-12-27T10:53:19.573494'
category: anomaly
severity: critical
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- critical
resolution_status: open
suggested_actions:
- Monitor system load and resource usage
- Check if requests are completing or getting stuck
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: active_requests_1766850799.573494
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 104.0
    baseline_value: 0.7364341085271318
    deviation: 15.805521556273103
    severity: critical
    percentage_change: 14022.105263157895
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

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 104.00
- **Baseline Value**: 0.74
- **Deviation**: 15.81 standard deviations
- **Change**: +14022.1%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

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

1. Monitor system load and resource usage
2. Check if requests are completing or getting stuck
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 104.0,
    "baseline_value": 0.7364341085271318,
    "deviation": 15.805521556273103,
    "severity": "critical",
    "percentage_change": 14022.105263157895
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

1. Monitor system load and resource usage
2. Check if requests are completing or getting stuck
3. Investigate immediately - critical system issue detected
