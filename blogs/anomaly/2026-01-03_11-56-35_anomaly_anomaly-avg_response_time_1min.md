---
timestamp: 1767459395.109992
datetime: '2026-01-03T11:56:35.109992'
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
  anomaly_id: avg_response_time_1min_1767459395.109992
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1658.9127381642659
    baseline_value: 564.3557729392217
    deviation: 4.696967902392185
    severity: critical
    percentage_change: 193.9480408828781
  system_state:
    active_requests: 1
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 1658.9127381642659
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1658.91
- **Baseline Value**: 564.36
- **Deviation**: 4.70 standard deviations
- **Change**: +193.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1658.91ms

### Efficiency Metrics

- **Requests/sec**: 0.10
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
    "current_value": 1658.9127381642659,
    "baseline_value": 564.3557729392217,
    "deviation": 4.696967902392185,
    "severity": "critical",
    "percentage_change": 193.9480408828781
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1658.9127381642659
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
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
