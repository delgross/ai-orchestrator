---
timestamp: 1767357330.997472
datetime: '2026-01-02T07:35:30.997472'
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
  anomaly_id: avg_response_time_1min_1767357330.997472
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 12707.036124335395
    baseline_value: 814.3713788567148
    deviation: 84.56275139264815
    severity: critical
    percentage_change: 1460.3490562468728
  system_state:
    active_requests: 1
    completed_requests_1min: 9
    error_rate_1min: 0.0
    avg_response_time_1min: 12707.036124335395
  metadata: {}
  efficiency:
    requests_per_second: 0.15
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 12707.04
- **Baseline Value**: 814.37
- **Deviation**: 84.56 standard deviations
- **Change**: +1460.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 9
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 12707.04ms

### Efficiency Metrics

- **Requests/sec**: 0.15
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
    "current_value": 12707.036124335395,
    "baseline_value": 814.3713788567148,
    "deviation": 84.56275139264815,
    "severity": "critical",
    "percentage_change": 1460.3490562468728
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 9,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 12707.036124335395
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.15,
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
