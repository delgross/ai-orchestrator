---
timestamp: 1767384064.774528
datetime: '2026-01-02T15:01:04.774528'
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
  anomaly_id: avg_response_time_1min_1767384064.774528
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 12538.44161828359
    baseline_value: 765.2710574738522
    deviation: 375.81989647277567
    severity: critical
    percentage_change: 1538.4314414911744
  system_state:
    active_requests: 3
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 12538.44161828359
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 12538.44
- **Baseline Value**: 765.27
- **Deviation**: 375.82 standard deviations
- **Change**: +1538.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 12538.44ms

### Efficiency Metrics

- **Requests/sec**: 0.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

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
    "current_value": 12538.44161828359,
    "baseline_value": 765.2710574738522,
    "deviation": 375.81989647277567,
    "severity": "critical",
    "percentage_change": 1538.4314414911744
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 12538.44161828359
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
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
