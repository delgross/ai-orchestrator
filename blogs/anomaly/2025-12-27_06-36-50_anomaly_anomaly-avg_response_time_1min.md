---
timestamp: 1766835410.339862
datetime: '2025-12-27T06:36:50.339862'
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
  anomaly_id: avg_response_time_1min_1766835410.339862
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 158.95488858222961
    baseline_value: 1.9804409170407813
    deviation: 10.784115831823138
    severity: critical
    percentage_change: 7926.23735020298
  system_state:
    active_requests: 0
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 158.95488858222961
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 158.95
- **Baseline Value**: 1.98
- **Deviation**: 10.78 standard deviations
- **Change**: +7926.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 158.95ms

### Efficiency Metrics

- **Requests/sec**: 0.13
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
    "current_value": 158.95488858222961,
    "baseline_value": 1.9804409170407813,
    "deviation": 10.784115831823138,
    "severity": "critical",
    "percentage_change": 7926.23735020298
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 158.95488858222961
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
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
