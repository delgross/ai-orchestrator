---
timestamp: 1766920447.9698648
datetime: '2025-12-28T06:14:07.969865'
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
  anomaly_id: avg_response_time_1min_1766920447.9698648
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 441.34236891058424
    baseline_value: 27.377913217963524
    deviation: 9.559393162157038
    severity: critical
    percentage_change: 1512.0380154503719
  system_state:
    active_requests: 1
    completed_requests_1min: 79
    error_rate_1min: 0.0
    avg_response_time_1min: 441.34236891058424
  metadata: {}
  efficiency:
    requests_per_second: 1.3166666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 441.34
- **Baseline Value**: 27.38
- **Deviation**: 9.56 standard deviations
- **Change**: +1512.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 79
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 441.34ms

### Efficiency Metrics

- **Requests/sec**: 1.32
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
    "current_value": 441.34236891058424,
    "baseline_value": 27.377913217963524,
    "deviation": 9.559393162157038,
    "severity": "critical",
    "percentage_change": 1512.0380154503719
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 79,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 441.34236891058424
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3166666666666667,
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
