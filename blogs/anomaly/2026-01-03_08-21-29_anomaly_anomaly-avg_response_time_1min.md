---
timestamp: 1767446489.366064
datetime: '2026-01-03T08:21:29.366064'
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
  anomaly_id: avg_response_time_1min_1767446489.366064
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1067.9516659842598
    baseline_value: 505.1815634151157
    deviation: 4.865360120559962
    severity: critical
    percentage_change: 111.39957261399638
  system_state:
    active_requests: 1
    completed_requests_1min: 18
    error_rate_1min: 0.0
    avg_response_time_1min: 1067.9516659842598
  metadata: {}
  efficiency:
    requests_per_second: 0.3
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1067.95
- **Baseline Value**: 505.18
- **Deviation**: 4.87 standard deviations
- **Change**: +111.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 18
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1067.95ms

### Efficiency Metrics

- **Requests/sec**: 0.30
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
    "current_value": 1067.9516659842598,
    "baseline_value": 505.1815634151157,
    "deviation": 4.865360120559962,
    "severity": "critical",
    "percentage_change": 111.39957261399638
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 18,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1067.9516659842598
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.3,
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
