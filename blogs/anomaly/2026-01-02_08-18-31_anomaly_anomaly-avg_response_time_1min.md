---
timestamp: 1767359911.795111
datetime: '2026-01-02T08:18:31.795111'
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
  anomaly_id: avg_response_time_1min_1767359911.795111
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 3381.9849157333374
    baseline_value: 814.7180182003626
    deviation: 17.810043171719098
    severity: critical
    percentage_change: 315.11109858645716
  system_state:
    active_requests: 1
    completed_requests_1min: 50
    error_rate_1min: 0.0
    avg_response_time_1min: 3381.9849157333374
  metadata: {}
  efficiency:
    requests_per_second: 0.8333333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 3381.98
- **Baseline Value**: 814.72
- **Deviation**: 17.81 standard deviations
- **Change**: +315.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 50
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3381.98ms

### Efficiency Metrics

- **Requests/sec**: 0.83
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
    "current_value": 3381.9849157333374,
    "baseline_value": 814.7180182003626,
    "deviation": 17.810043171719098,
    "severity": "critical",
    "percentage_change": 315.11109858645716
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 50,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3381.9849157333374
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8333333333333334,
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
