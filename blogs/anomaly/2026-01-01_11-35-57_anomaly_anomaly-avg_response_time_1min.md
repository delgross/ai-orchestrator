---
timestamp: 1767285357.055027
datetime: '2026-01-01T11:35:57.055027'
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
  anomaly_id: avg_response_time_1min_1767285357.055027
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1151.2301594018936
    baseline_value: 378.17135038255134
    deviation: 3.2821696632301505
    severity: critical
    percentage_change: 204.42024712800958
  system_state:
    active_requests: 6
    completed_requests_1min: 81
    error_rate_1min: 0.0
    avg_response_time_1min: 1137.3633219871992
  metadata: {}
  efficiency:
    requests_per_second: 1.35
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1151.23
- **Baseline Value**: 378.17
- **Deviation**: 3.28 standard deviations
- **Change**: +204.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 81
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1137.36ms

### Efficiency Metrics

- **Requests/sec**: 1.35
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

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
    "current_value": 1151.2301594018936,
    "baseline_value": 378.17135038255134,
    "deviation": 3.2821696632301505,
    "severity": "critical",
    "percentage_change": 204.42024712800958
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 81,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1137.3633219871992
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.35,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
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
