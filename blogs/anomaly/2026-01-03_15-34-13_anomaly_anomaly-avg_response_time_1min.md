---
timestamp: 1767472453.558184
datetime: '2026-01-03T15:34:13.558184'
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
  anomaly_id: avg_response_time_1min_1767472453.558184
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4736.746766350486
    baseline_value: 521.7536025577122
    deviation: 8.078512813577643
    severity: critical
    percentage_change: 807.8512813577643
  system_state:
    active_requests: 0
    completed_requests_1min: 11
    error_rate_1min: 0.0
    avg_response_time_1min: 4736.746766350486
  metadata: {}
  efficiency:
    requests_per_second: 0.18333333333333332
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4736.75
- **Baseline Value**: 521.75
- **Deviation**: 8.08 standard deviations
- **Change**: +807.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 11
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4736.75ms

### Efficiency Metrics

- **Requests/sec**: 0.18
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
    "current_value": 4736.746766350486,
    "baseline_value": 521.7536025577122,
    "deviation": 8.078512813577643,
    "severity": "critical",
    "percentage_change": 807.8512813577643
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 11,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4736.746766350486
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.18333333333333332,
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
