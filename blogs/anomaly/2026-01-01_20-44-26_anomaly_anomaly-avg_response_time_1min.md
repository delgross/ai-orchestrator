---
timestamp: 1767318266.1571891
datetime: '2026-01-01T20:44:26.157189'
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
  anomaly_id: avg_response_time_1min_1767318266.1571891
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 749.6555063984182
    baseline_value: 257.7115512952056
    deviation: 4.960325327805758
    severity: critical
    percentage_change: 190.88936938635572
  system_state:
    active_requests: 1
    completed_requests_1min: 101
    error_rate_1min: 0.0
    avg_response_time_1min: 749.6555063984182
  metadata: {}
  efficiency:
    requests_per_second: 1.6833333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 749.66
- **Baseline Value**: 257.71
- **Deviation**: 4.96 standard deviations
- **Change**: +190.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 101
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 749.66ms

### Efficiency Metrics

- **Requests/sec**: 1.68
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
    "current_value": 749.6555063984182,
    "baseline_value": 257.7115512952056,
    "deviation": 4.960325327805758,
    "severity": "critical",
    "percentage_change": 190.88936938635572
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 101,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 749.6555063984182
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6833333333333333,
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
