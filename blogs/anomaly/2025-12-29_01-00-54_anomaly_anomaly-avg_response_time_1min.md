---
timestamp: 1766988054.763499
datetime: '2025-12-29T01:00:54.763499'
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
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1766988054.763499
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 646.0561338736087
    baseline_value: 155.97583925954726
    deviation: 31.2896805049171
    severity: critical
    percentage_change: 314.20269763611077
  system_state:
    active_requests: 1
    completed_requests_1min: 98
    error_rate_1min: 0.0
    avg_response_time_1min: 646.0561338736087
  metadata: {}
  efficiency:
    requests_per_second: 1.6333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 646.06
- **Baseline Value**: 155.98
- **Deviation**: 31.29 standard deviations
- **Change**: +314.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 98
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 646.06ms

### Efficiency Metrics

- **Requests/sec**: 1.63
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 646.0561338736087,
    "baseline_value": 155.97583925954726,
    "deviation": 31.2896805049171,
    "severity": "critical",
    "percentage_change": 314.20269763611077
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 98,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 646.0561338736087
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6333333333333333,
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
3. Investigate immediately - critical system issue detected
