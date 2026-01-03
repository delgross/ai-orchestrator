---
timestamp: 1767453511.817478
datetime: '2026-01-03T10:18:31.817478'
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
  anomaly_id: avg_response_time_1min_1767453511.817478
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1663.909843989781
    baseline_value: 485.2072161932786
    deviation: 8.327998076587503
    severity: critical
    percentage_change: 242.92767882639552
  system_state:
    active_requests: 0
    completed_requests_1min: 7
    error_rate_1min: 0.0
    avg_response_time_1min: 1663.909843989781
  metadata: {}
  efficiency:
    requests_per_second: 0.11666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1663.91
- **Baseline Value**: 485.21
- **Deviation**: 8.33 standard deviations
- **Change**: +242.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 7
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1663.91ms

### Efficiency Metrics

- **Requests/sec**: 0.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

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
    "current_value": 1663.909843989781,
    "baseline_value": 485.2072161932786,
    "deviation": 8.327998076587503,
    "severity": "critical",
    "percentage_change": 242.92767882639552
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 7,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1663.909843989781
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.11666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
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
