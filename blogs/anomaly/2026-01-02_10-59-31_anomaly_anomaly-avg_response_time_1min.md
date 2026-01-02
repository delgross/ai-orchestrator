---
timestamp: 1767369571.177943
datetime: '2026-01-02T10:59:31.177943'
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
  anomaly_id: avg_response_time_1min_1767369571.177943
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5587.409025879317
    baseline_value: 2067.3207203087777
    deviation: 3.147566739806346
    severity: critical
    percentage_change: 170.27296592106782
  system_state:
    active_requests: 11
    completed_requests_1min: 186
    error_rate_1min: 0.0
    avg_response_time_1min: 5587.409025879317
  metadata: {}
  efficiency:
    requests_per_second: 3.1
    cache_hit_rate: 0.0
    queue_depth: 11
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5587.41
- **Baseline Value**: 2067.32
- **Deviation**: 3.15 standard deviations
- **Change**: +170.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 11
- **Completed Requests (1min)**: 186
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 5587.41ms

### Efficiency Metrics

- **Requests/sec**: 3.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 11

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
    "current_value": 5587.409025879317,
    "baseline_value": 2067.3207203087777,
    "deviation": 3.147566739806346,
    "severity": "critical",
    "percentage_change": 170.27296592106782
  },
  "system_state": {
    "active_requests": 11,
    "completed_requests_1min": 186,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 5587.409025879317
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.1,
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
4. Investigate immediately - critical system issue detected
