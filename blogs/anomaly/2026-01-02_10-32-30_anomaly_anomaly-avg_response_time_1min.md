---
timestamp: 1767367950.761248
datetime: '2026-01-02T10:32:30.761248'
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
  anomaly_id: avg_response_time_1min_1767367950.761248
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4451.169907617912
    baseline_value: 1926.277536480159
    deviation: 6.105677205356081
    severity: critical
    percentage_change: 131.07625060880005
  system_state:
    active_requests: 9
    completed_requests_1min: 139
    error_rate_1min: 0.0
    avg_response_time_1min: 4451.169907617912
  metadata: {}
  efficiency:
    requests_per_second: 2.316666666666667
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4451.17
- **Baseline Value**: 1926.28
- **Deviation**: 6.11 standard deviations
- **Change**: +131.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 139
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4451.17ms

### Efficiency Metrics

- **Requests/sec**: 2.32
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

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
    "current_value": 4451.169907617912,
    "baseline_value": 1926.277536480159,
    "deviation": 6.105677205356081,
    "severity": "critical",
    "percentage_change": 131.07625060880005
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 139,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4451.169907617912
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.316666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
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
