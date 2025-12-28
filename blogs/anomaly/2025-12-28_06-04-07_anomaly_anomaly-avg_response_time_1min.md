---
timestamp: 1766919847.9339
datetime: '2025-12-28T06:04:07.933900'
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
  anomaly_id: avg_response_time_1min_1766919847.9339
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 303.3328525355605
    baseline_value: 22.79947522341387
    deviation: 13.527921397764837
    severity: critical
    percentage_change: 1230.4378700087514
  system_state:
    active_requests: 1
    completed_requests_1min: 61
    error_rate_1min: 0.0
    avg_response_time_1min: 303.3328525355605
  metadata: {}
  efficiency:
    requests_per_second: 1.0166666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 303.33
- **Baseline Value**: 22.80
- **Deviation**: 13.53 standard deviations
- **Change**: +1230.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 61
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 303.33ms

### Efficiency Metrics

- **Requests/sec**: 1.02
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
    "current_value": 303.3328525355605,
    "baseline_value": 22.79947522341387,
    "deviation": 13.527921397764837,
    "severity": "critical",
    "percentage_change": 1230.4378700087514
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 61,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 303.3328525355605
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0166666666666666,
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
