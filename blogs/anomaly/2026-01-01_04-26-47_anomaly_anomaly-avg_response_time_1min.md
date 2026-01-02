---
timestamp: 1767259607.465297
datetime: '2026-01-01T04:26:47.465297'
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
  anomaly_id: avg_response_time_1min_1767259607.465297
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1785.5754140494525
    baseline_value: 556.4830196437551
    deviation: 4.13944841361855
    severity: critical
    percentage_change: 220.86790630063211
  system_state:
    active_requests: 1
    completed_requests_1min: 69
    error_rate_1min: 0.0
    avg_response_time_1min: 1785.5754140494525
  metadata: {}
  efficiency:
    requests_per_second: 1.15
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1785.58
- **Baseline Value**: 556.48
- **Deviation**: 4.14 standard deviations
- **Change**: +220.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 69
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1785.58ms

### Efficiency Metrics

- **Requests/sec**: 1.15
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
    "current_value": 1785.5754140494525,
    "baseline_value": 556.4830196437551,
    "deviation": 4.13944841361855,
    "severity": "critical",
    "percentage_change": 220.86790630063211
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 69,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1785.5754140494525
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.15,
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
