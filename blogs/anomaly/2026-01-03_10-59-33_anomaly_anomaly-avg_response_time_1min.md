---
timestamp: 1767455973.218425
datetime: '2026-01-03T10:59:33.218425'
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
  anomaly_id: avg_response_time_1min_1767455973.218425
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1952.8191685676575
    baseline_value: 494.2722211634447
    deviation: 9.695686160511308
    severity: critical
    percentage_change: 295.0898077927596
  system_state:
    active_requests: 0
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 1952.8191685676575
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1952.82
- **Baseline Value**: 494.27
- **Deviation**: 9.70 standard deviations
- **Change**: +295.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1952.82ms

### Efficiency Metrics

- **Requests/sec**: 0.07
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
    "current_value": 1952.8191685676575,
    "baseline_value": 494.2722211634447,
    "deviation": 9.695686160511308,
    "severity": "critical",
    "percentage_change": 295.0898077927596
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1952.8191685676575
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
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
