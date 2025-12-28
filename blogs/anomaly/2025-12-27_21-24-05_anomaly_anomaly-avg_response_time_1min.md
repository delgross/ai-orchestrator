---
timestamp: 1766888645.6069639
datetime: '2025-12-27T21:24:05.606964'
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
  anomaly_id: avg_response_time_1min_1766888645.6069639
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 805.6398408357487
    baseline_value: 133.5630850302107
    deviation: 15.063799956115965
    severity: critical
    percentage_change: 503.19050031939645
  system_state:
    active_requests: 1
    completed_requests_1min: 86
    error_rate_1min: 0.0
    avg_response_time_1min: 805.6398408357487
  metadata: {}
  efficiency:
    requests_per_second: 1.4333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 805.64
- **Baseline Value**: 133.56
- **Deviation**: 15.06 standard deviations
- **Change**: +503.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 86
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 805.64ms

### Efficiency Metrics

- **Requests/sec**: 1.43
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
    "current_value": 805.6398408357487,
    "baseline_value": 133.5630850302107,
    "deviation": 15.063799956115965,
    "severity": "critical",
    "percentage_change": 503.19050031939645
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 86,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 805.6398408357487
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.4333333333333333,
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
