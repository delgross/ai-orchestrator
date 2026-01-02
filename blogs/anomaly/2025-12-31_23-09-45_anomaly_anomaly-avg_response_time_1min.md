---
timestamp: 1767240585.8696609
datetime: '2025-12-31T23:09:45.869661'
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
  anomaly_id: avg_response_time_1min_1767240585.8696609
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2582.722043991089
    baseline_value: 180.44201020271547
    deviation: 187.9345519241845
    severity: critical
    percentage_change: 1331.3307865998388
  system_state:
    active_requests: 2
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 2582.722043991089
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2582.72
- **Baseline Value**: 180.44
- **Deviation**: 187.93 standard deviations
- **Change**: +1331.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2582.72ms

### Efficiency Metrics

- **Requests/sec**: 0.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

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
    "current_value": 2582.722043991089,
    "baseline_value": 180.44201020271547,
    "deviation": 187.9345519241845,
    "severity": "critical",
    "percentage_change": 1331.3307865998388
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2582.722043991089
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
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
