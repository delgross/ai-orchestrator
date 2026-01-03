---
timestamp: 1767382864.272047
datetime: '2026-01-02T14:41:04.272047'
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
  anomaly_id: avg_response_time_1min_1767382864.272047
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 16548.301696777344
    baseline_value: 764.1909116117678
    deviation: 522.7092183504205
    severity: critical
    percentage_change: 2065.466959280508
  system_state:
    active_requests: 4
    completed_requests_1min: 14
    error_rate_1min: 0.0
    avg_response_time_1min: 16548.301696777344
  metadata: {}
  efficiency:
    requests_per_second: 0.23333333333333334
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 16548.30
- **Baseline Value**: 764.19
- **Deviation**: 522.71 standard deviations
- **Change**: +2065.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 14
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 16548.30ms

### Efficiency Metrics

- **Requests/sec**: 0.23
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

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
    "current_value": 16548.301696777344,
    "baseline_value": 764.1909116117678,
    "deviation": 522.7092183504205,
    "severity": "critical",
    "percentage_change": 2065.466959280508
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 14,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 16548.301696777344
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.23333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
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
