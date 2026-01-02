---
timestamp: 1767358711.403625
datetime: '2026-01-02T07:58:31.403625'
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
  anomaly_id: avg_response_time_1min_1767358711.403625
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5818.2944701268125
    baseline_value: 814.5912093582864
    deviation: 35.04642591307996
    severity: critical
    percentage_change: 614.2594227981311
  system_state:
    active_requests: 0
    completed_requests_1min: 13
    error_rate_1min: 0.0
    avg_response_time_1min: 5818.2944701268125
  metadata: {}
  efficiency:
    requests_per_second: 0.21666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5818.29
- **Baseline Value**: 814.59
- **Deviation**: 35.05 standard deviations
- **Change**: +614.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 13
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 5818.29ms

### Efficiency Metrics

- **Requests/sec**: 0.22
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
    "current_value": 5818.2944701268125,
    "baseline_value": 814.5912093582864,
    "deviation": 35.04642591307996,
    "severity": "critical",
    "percentage_change": 614.2594227981311
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 13,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 5818.2944701268125
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.21666666666666667,
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
