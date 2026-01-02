---
timestamp: 1767358411.3203058
datetime: '2026-01-02T07:53:31.320306'
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
  anomaly_id: avg_response_time_1min_1767358411.3203058
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1688.014344735579
    baseline_value: 814.6574430554589
    deviation: 6.143997317364041
    severity: critical
    percentage_change: 107.20541610772041
  system_state:
    active_requests: 1
    completed_requests_1min: 22
    error_rate_1min: 0.0
    avg_response_time_1min: 1688.014344735579
  metadata: {}
  efficiency:
    requests_per_second: 0.36666666666666664
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1688.01
- **Baseline Value**: 814.66
- **Deviation**: 6.14 standard deviations
- **Change**: +107.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 22
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1688.01ms

### Efficiency Metrics

- **Requests/sec**: 0.37
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
    "current_value": 1688.014344735579,
    "baseline_value": 814.6574430554589,
    "deviation": 6.143997317364041,
    "severity": "critical",
    "percentage_change": 107.20541610772041
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 22,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1688.014344735579
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.36666666666666664,
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
