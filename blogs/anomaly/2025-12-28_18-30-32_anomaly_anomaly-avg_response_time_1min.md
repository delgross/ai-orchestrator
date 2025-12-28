---
timestamp: 1766964632.78867
datetime: '2025-12-28T18:30:32.788670'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
metadata:
  anomaly_id: avg_response_time_1min_1766964632.78867
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 662.1079859526261
    baseline_value: 160.39092751812186
    deviation: 5.600166992238774
    severity: warning
    percentage_change: 312.80887653562417
  system_state:
    active_requests: 0
    completed_requests_1min: 92
    error_rate_1min: 0.0
    avg_response_time_1min: 662.1079859526261
  metadata: {}
  efficiency:
    requests_per_second: 1.5333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 662.11
- **Baseline Value**: 160.39
- **Deviation**: 5.60 standard deviations
- **Change**: +312.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 92
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 662.11ms

### Efficiency Metrics

- **Requests/sec**: 1.53
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 662.1079859526261,
    "baseline_value": 160.39092751812186,
    "deviation": 5.600166992238774,
    "severity": "warning",
    "percentage_change": 312.80887653562417
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 92,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 662.1079859526261
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5333333333333334,
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
