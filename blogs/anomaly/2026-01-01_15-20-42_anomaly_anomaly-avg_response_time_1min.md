---
timestamp: 1767298842.5384629
datetime: '2026-01-01T15:20:42.538463'
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
  anomaly_id: avg_response_time_1min_1767298842.5384629
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 7330.557386080424
    baseline_value: 1218.5772584832232
    deviation: 8.374874009414786
    severity: critical
    percentage_change: 501.56689574240465
  system_state:
    active_requests: 2
    completed_requests_1min: 12
    error_rate_1min: 0.0
    avg_response_time_1min: 7330.557386080424
  metadata: {}
  efficiency:
    requests_per_second: 0.2
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 7330.56
- **Baseline Value**: 1218.58
- **Deviation**: 8.37 standard deviations
- **Change**: +501.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 12
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 7330.56ms

### Efficiency Metrics

- **Requests/sec**: 0.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

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
    "current_value": 7330.557386080424,
    "baseline_value": 1218.5772584832232,
    "deviation": 8.374874009414786,
    "severity": "critical",
    "percentage_change": 501.56689574240465
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 12,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 7330.557386080424
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
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
