---
timestamp: 1766923268.130025
datetime: '2025-12-28T07:01:08.130025'
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
  anomaly_id: avg_response_time_1min_1766923268.130025
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1060.1495668805878
    baseline_value: 41.67015335870608
    deviation: 10.658447935661982
    severity: critical
    percentage_change: 2444.1460648214593
  system_state:
    active_requests: 1
    completed_requests_1min: 58
    error_rate_1min: 0.0
    avg_response_time_1min: 1060.1495668805878
  metadata: {}
  efficiency:
    requests_per_second: 0.9666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1060.15
- **Baseline Value**: 41.67
- **Deviation**: 10.66 standard deviations
- **Change**: +2444.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 58
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1060.15ms

### Efficiency Metrics

- **Requests/sec**: 0.97
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
    "current_value": 1060.1495668805878,
    "baseline_value": 41.67015335870608,
    "deviation": 10.658447935661982,
    "severity": "critical",
    "percentage_change": 2444.1460648214593
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 58,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1060.1495668805878
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9666666666666667,
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
