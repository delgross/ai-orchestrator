---
timestamp: 1766920147.9491708
datetime: '2025-12-28T06:09:07.949171'
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
  anomaly_id: avg_response_time_1min_1766920147.9491708
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 434.2475168166622
    baseline_value: 25.008879858387566
    deviation: 12.396512849042287
    severity: critical
    percentage_change: 1636.373317300026
  system_state:
    active_requests: 1
    completed_requests_1min: 62
    error_rate_1min: 0.0
    avg_response_time_1min: 434.2475168166622
  metadata: {}
  efficiency:
    requests_per_second: 1.0333333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 434.25
- **Baseline Value**: 25.01
- **Deviation**: 12.40 standard deviations
- **Change**: +1636.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 62
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 434.25ms

### Efficiency Metrics

- **Requests/sec**: 1.03
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
    "current_value": 434.2475168166622,
    "baseline_value": 25.008879858387566,
    "deviation": 12.396512849042287,
    "severity": "critical",
    "percentage_change": 1636.373317300026
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 62,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 434.2475168166622
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0333333333333334,
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
