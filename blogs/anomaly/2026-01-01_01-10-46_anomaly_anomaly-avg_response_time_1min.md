---
timestamp: 1767247846.554278
datetime: '2026-01-01T01:10:46.554278'
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
  anomaly_id: avg_response_time_1min_1767247846.554278
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 461.47307895478747
    baseline_value: 218.9333008395301
    deviation: 4.799886671032615
    severity: critical
    percentage_change: 110.78249731091843
  system_state:
    active_requests: 0
    completed_requests_1min: 63
    error_rate_1min: 0.0
    avg_response_time_1min: 461.47307895478747
  metadata: {}
  efficiency:
    requests_per_second: 1.05
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 461.47
- **Baseline Value**: 218.93
- **Deviation**: 4.80 standard deviations
- **Change**: +110.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 63
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 461.47ms

### Efficiency Metrics

- **Requests/sec**: 1.05
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
    "current_value": 461.47307895478747,
    "baseline_value": 218.9333008395301,
    "deviation": 4.799886671032615,
    "severity": "critical",
    "percentage_change": 110.78249731091843
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 63,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 461.47307895478747
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.05,
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
