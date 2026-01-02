---
timestamp: 1767247486.524686
datetime: '2026-01-01T01:04:46.524686'
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
  anomaly_id: avg_response_time_1min_1767247486.524686
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 505.34104334341515
    baseline_value: 195.46735671258742
    deviation: 10.019758511624884
    severity: critical
    percentage_change: 158.52963473919678
  system_state:
    active_requests: 0
    completed_requests_1min: 74
    error_rate_1min: 0.0
    avg_response_time_1min: 505.34104334341515
  metadata: {}
  efficiency:
    requests_per_second: 1.2333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 505.34
- **Baseline Value**: 195.47
- **Deviation**: 10.02 standard deviations
- **Change**: +158.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 74
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 505.34ms

### Efficiency Metrics

- **Requests/sec**: 1.23
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
    "current_value": 505.34104334341515,
    "baseline_value": 195.46735671258742,
    "deviation": 10.019758511624884,
    "severity": "critical",
    "percentage_change": 158.52963473919678
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 74,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 505.34104334341515
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.2333333333333334,
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
